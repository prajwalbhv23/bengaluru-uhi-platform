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
    print("Rebuilding database schemas for platform.db...")
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    
    # Check if we already have seeded data
    existing = db.query(models.UploadDataset).filter(
        (models.UploadDataset.filename == "Bangalore_UHI_Production.csv") |
        (models.UploadDataset.filename == "Bengaluru_UHI_Production.csv") |
        (models.UploadDataset.is_default == True)
    ).first()
    if existing:
        print("Database already seeded with Bangalore_UHI_Production.csv.")
        db.close()
        return

    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "samples", "Bangalore_UHI_Production.csv")
    if not os.path.exists(csv_path):
        print(f"Error: Seed file not found at {csv_path}. Please generate it first.")
        db.close()
        return
        
    print(f"Reading seed coordinates from {csv_path}...")
    predictions = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            lst_val = float(row["lst"])
            ndvi_val = float(row["ndvi"])
            ndbi_val = float(row["ndbi"])
            
            # Predict risk and growth prediction
            risk_score = min(100.0, max(0.0, (lst_val - 20.0) / 28.0 * 100.0))
            risk_lvl = "Critical" if lst_val >= 41.0 else "High" if lst_val >= 35.0 else "Medium" if lst_val >= 28.0 else "Low"
            growth = max(0.1, round((ndbi_val - ndvi_val) * 1.2 + 0.8, 2))
            
            predictions.append({
                "name": row["name"],
                "ward": row["ward"],
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
                "lst": lst_val,
                "ndvi": ndvi_val,
                "ndbi": ndbi_val,
                "tree_canopy": float(row["tree_canopy"]),
                "population_density": float(row["population_density"]),
                "land_cover": row["land_cover"],
                "risk_score": round(risk_score, 1),
                "risk_level": risk_lvl,
                "growth_prediction": growth
            })
            
    # Calculate dataset statistics
    lsts = [p["lst"] for p in predictions]
    avg_temp = sum(lsts) / len(lsts)
    min_temp = min(lsts)
    max_temp = max(lsts)
    water_count = sum(1 for p in predictions if p["land_cover"].lower() == "water")
    water_body_coverage = (water_count / len(predictions)) * 100
    heat_island_intensity = max_temp - min_temp
    
    print("Creating UploadDataset record for Bangalore_UHI_Production.csv...")
    dataset = models.UploadDataset(
        filename="Bangalore_UHI_Production.csv",
        file_type="csv",
        status="Processed",
        is_default=True,
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
        # Calculate local humidity and heat index
        humidity = max(15.0, min(95.0, 40.0 + pred["ndvi"] * 50.0))
        air_temp = pred["lst"] - 3.5
        heat_index = air_temp  # simplified model same as routes/map.py
        
        hotspot = models.HotspotPrediction(
            dataset_id=dataset.id,
            name=pred["name"],
            ward=pred["ward"],
            latitude=pred["latitude"],
            longitude=pred["longitude"],
            lst=pred["lst"],
            ndvi=pred["ndvi"],
            ndbi=pred["ndbi"],
            built_up_density=round((pred["ndbi"] + 1) * 50.0, 1),
            vegetation_density=round((pred["ndvi"] + 1) * 50.0, 1),
            tree_canopy=pred["tree_canopy"],
            population_density=pred["population_density"],
            humidity=round(humidity, 1),
            heat_index=round(heat_index, 1),
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
