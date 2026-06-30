import os
import sys
import csv
from sqlalchemy.orm import Session

# Add backend directory to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine, Base
import models
from recommendation_engine.engine import AIRecommendationEngine

def seed():
    print("Rebuilding database schemas for platform_v2...")
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    
    # Check if we already have seeded data
    existing = db.query(models.UploadDataset).filter(models.UploadDataset.filename == "Bengaluru_Sentinel2.tif").first()
    if existing:
        print("Database already seeded with Bengaluru_Sentinel2.tif.")
        db.close()
        return

    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "samples", "bangalore_complete_uhi.csv")
    if not os.path.exists(csv_path):
        print(f"Error: Seed file not found at {csv_path}. Please run generate_samples.py first.")
        db.close()
        return
        
    print(f"Reading seed coordinates from {csv_path}...")
    predictions = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            predictions.append({
                "name": row["name"],
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
                "lst": float(row["lst"]),
                "ndvi": float(row["ndvi"]),
                "ndbi": float(row["ndbi"]),
                "land_cover": row["land_cover"],
                "risk_score": float(row["lst"]) * 2.0, # basic score mapping
                "risk_level": "Critical" if float(row["lst"]) >= 42.0 else "High" if float(row["lst"]) >= 35.0 else "Medium" if float(row["lst"]) >= 28.0 else "Low",
                "growth_prediction": float(row["lst"]) + 1.2
            })
            
    # Calculate dataset statistics
    lsts = [p["lst"] for p in predictions]
    avg_temp = sum(lsts) / len(lsts)
    min_temp = min(lsts)
    max_temp = max(lsts)
    water_count = sum(1 for p in predictions if p["land_cover"].lower() == "water")
    water_body_coverage = (water_count / len(predictions)) * 100
    heat_island_intensity = max_temp - min_temp
    
    print("Creating UploadDataset record for Bengaluru_Sentinel2.tif...")
    dataset = models.UploadDataset(
        filename="Bengaluru_Sentinel2.tif",
        file_type="tif",
        status="Processed",
        records_count=len(predictions),
        file_path=csv_path,
        avg_temp=round(avg_temp, 2),
        min_temp=round(min_temp, 2),
        max_temp=round(max_temp, 2),
        water_body_coverage=round(water_body_coverage, 2),
        heat_island_intensity=round(heat_island_intensity, 2)
    )
    db.add(dataset)
    db.flush() # populate dataset.id
    
    print(f"Inserting {len(predictions)} hotspots and generating recommendations...")
    for pred in predictions:
        hotspot = models.HotspotPrediction(
            dataset_id=dataset.id,
            name=pred["name"],
            latitude=pred["latitude"],
            longitude=pred["longitude"],
            lst=pred["lst"],
            ndvi=pred["ndvi"],
            ndbi=pred["ndbi"],
            built_up_density=round((pred["ndbi"] + 1) * 50.0, 1),
            vegetation_density=round((pred["ndvi"] + 1) * 50.0, 1),
            risk_score=pred["risk_score"],
            risk_level=pred["risk_level"],
            growth_prediction=pred["growth_prediction"],
            land_cover=pred["land_cover"]
        )
        db.add(hotspot)
        db.flush()
        
        # Generate dynamic recommendations for this hotspot
        recs = AIRecommendationEngine.generate_recommendations(pred, water_body_coverage=water_body_coverage)
        for r in recs:
            recommendation = models.MitigationRecommendation(
                hotspot_id=hotspot.id,
                strategy_name=r.get("strategy_name"),
                category=r.get("category"),
                description=r.get("strategy_name"),
                confidence_score=r.get("confidence_score", 90.0),
                temp_reduction=r.get("temp_reduction", 1.5),
                cost_est=15.0 if r.get("cost_level") == "Low" else 50.0 if r.get("cost_level") == "Medium" else 150.0,
                env_impact=r.get("severity", "High"),
                carbon_reduction=12.0 if r.get("category") == "Cool Materials" else 25.0,
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
            
    # Compile dynamic report summary
    stats_dict = {"filename": dataset.filename}
    mitigation_summary_text = AIRecommendationEngine.generate_mitigation_summary(stats_dict, predictions)
    dataset.mitigation_summary = mitigation_summary_text
    
    db.commit()
    print("Database seeding completed successfully.")
    db.close()

if __name__ == "__main__":
    seed()
