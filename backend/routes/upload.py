import os
from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import UploadDataset, HotspotPrediction, MitigationRecommendation
from utils.geo_processor import process_uploaded_file, validate_file_structure
from ml.pipeline import MLPipeline
from recommendation_engine.engine import AIRecommendationEngine

router = APIRouter(prefix="/api")

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def process_dataset_background(dataset_id: int, file_path: str, file_type: str, db: Session):
    try:
        # 1. Parse file and extract features
        records = process_uploaded_file(file_path, file_type)
        
        if not records:
            raise ValueError("No valid spatial records found in file.")
            
        # 2. Run ML Pipeline: Train models on new data and predict metrics
        pipeline = MLPipeline()
        pipeline.train(records)
        predictions = pipeline.predict(records)
        
        # Calculate dataset statistics
        lsts = [p["lst"] for p in predictions]
        avg_temp = sum(lsts) / len(lsts)
        min_temp = min(lsts)
        max_temp = max(lsts)
        water_count = sum(1 for p in predictions if p["land_cover"].lower() == "water")
        water_body_coverage = (water_count / len(predictions)) * 100
        heat_island_intensity = max_temp - min_temp
        
        # 3. Save predicted hotspots and recommendations to DB
        for i, pred in enumerate(predictions):
            hotspot = HotspotPrediction(
                dataset_id=dataset_id,
                name=pred["name"],
                latitude=pred["latitude"],
                longitude=pred["longitude"],
                lst=pred["lst"],
                ndvi=pred["ndvi"],
                ndbi=pred["ndbi"],
                built_up_density=pred["built_up_density"],
                vegetation_density=pred["vegetation_density"],
                risk_score=pred["risk_score"],
                risk_level=pred["risk_level"],
                growth_prediction=pred["growth_prediction"],
                land_cover=pred["land_cover"]
            )
            db.add(hotspot)
            db.flush() # Populate hotspot ID
            
            # Generate and save dynamic recommendations
            recs = AIRecommendationEngine.generate_recommendations(pred, water_body_coverage=water_body_coverage)
            for r in recs:
                recommendation = MitigationRecommendation(
                    hotspot_id=hotspot.id,
                    strategy_name=r.get("strategy_name"),
                    category=r.get("category"),
                    description=r.get("strategy_name"), # fallback description is name
                    confidence_score=r.get("confidence_score", 90.0),
                    temp_reduction=r.get("temp_reduction", 1.5),
                    cost_est=15.0 if r.get("cost_level") == "Low" else 50.0 if r.get("cost_level") == "Medium" else 150.0, # numeric fallback
                    env_impact=r.get("severity", "High"), # Severity mapper
                    carbon_reduction=12.0 if r.get("category") == "Cool Materials" else 25.0, # fallback carbon metric
                    priority_level=r.get("priority_level", "Short Term"),
                    reason=r.get("reason", ""),
                    severity=r.get("severity", "High"),
                    estimated_impact=r.get("estimated_impact", "Improves local microclimate comfort."),
                    environmental_benefits=r.get("environmental_benefits", "Lower surface temperature"),
                    sdg_alignment=r.get("sdg_alignment", "SDG 11"),
                    cost_level=r.get("cost_level", "Medium"),
                    implementation_time=r.get("implementation_time", "6-12 months"),
                    technical_explanation=r.get("technical_explanation", "Albedo reflection or plant transpiration."),
                    sustainability_benefits=r.get("sustainability_benefits", "SDG 11: Sustainable Cities"),
                    recommended_implementation=r.get("recommended_implementation", "Implement cooling infrastructure."),
                    trigger_condition=r.get("trigger_condition", "LST > 30°C")
                )
                db.add(recommendation)
                
        # Compile global summary stats
        dataset = db.query(UploadDataset).filter(UploadDataset.id == dataset_id).first()
        dataset.status = "Processed"
        dataset.records_count = len(predictions)
        dataset.avg_temp = round(avg_temp, 2)
        dataset.min_temp = round(min_temp, 2)
        dataset.max_temp = round(max_temp, 2)
        dataset.water_body_coverage = round(water_body_coverage, 2)
        dataset.heat_island_intensity = round(heat_island_intensity, 2)
        
        # Build synthesis text block
        stats_dict = {"filename": dataset.filename}
        mitigation_summary_text = AIRecommendationEngine.generate_mitigation_summary(stats_dict, predictions)
        dataset.mitigation_summary = mitigation_summary_text
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        dataset = db.query(UploadDataset).filter(UploadDataset.id == dataset_id).first()
        if dataset:
            dataset.status = "Failed"
            db.commit()
        print(f"Background processing error: {e}")

@router.post("/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    filename = file.filename
    ext = filename.split(".")[-1].lower()
    
    if ext not in ["csv", "geojson", "tif", "tiff", "geotiff", "png", "jpg", "jpeg"]:
        raise HTTPException(status_code=400, detail="Unsupported file format.")
        
    # Save uploaded file
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
        
    # Synchronously validate structural and semantic requirements
    try:
        validate_file_structure(file_path, ext)
    except ValueError as val_err:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as general_err:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=400, detail=f"File validation error: {str(general_err)}")
        
    # Create DB entry
    db_dataset = UploadDataset(
        filename=filename,
        file_type=ext,
        file_path=file_path,
        status="Processing"
    )
    db.add(db_dataset)
    db.commit()
    db.refresh(db_dataset)
    
    # Process in background
    background_tasks.add_task(
        process_dataset_background,
        db_dataset.id,
        file_path,
        ext,
        db
    )
    
    return {
        "message": "File uploaded successfully. Processing started in background.",
        "dataset_id": db_dataset.id,
        "filename": filename,
        "status": "Processing"
    }
