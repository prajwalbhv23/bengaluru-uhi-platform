from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import UploadDataset, HotspotPrediction, MitigationRecommendation

router = APIRouter(prefix="/api")

@router.get("/recommendations")
async def get_all_recommendations(dataset_id: int = None, db: Session = Depends(get_db)):
    """
    Returns recommendations generated for hotspots. Can filter by dataset_id.
    """
    query = db.query(MitigationRecommendation).join(HotspotPrediction)
    
    if dataset_id:
        query = query.filter(HotspotPrediction.dataset_id == dataset_id)
        
    recs = query.all()
    
    results = []
    for r in recs:
        hotspot = r.hotspot
        results.append({
            "id": r.id,
            "hotspot_id": r.hotspot_id,
            "hotspot_name": hotspot.name,
            "lst": hotspot.lst,
            "land_cover": hotspot.land_cover,
            "strategy_name": r.strategy_name,
            "category": r.category,
            "description": r.description,
            "confidence_score": r.confidence_score,
            "temp_reduction": r.temp_reduction,
            "cost_est": r.cost_est,
            "env_impact": r.env_impact,
            "carbon_reduction": r.carbon_reduction,
            "priority_level": r.priority_level,
            "reason": r.reason,
            "severity": r.severity,
            "estimated_impact": r.estimated_impact,
            "environmental_benefits": r.environmental_benefits,
            "sdg_alignment": r.sdg_alignment,
            "cost_level": r.cost_level,
            "implementation_time": r.implementation_time,
            "technical_explanation": r.technical_explanation,
            "sustainability_benefits": r.sustainability_benefits,
            "recommended_implementation": r.recommended_implementation,
            "trigger_condition": r.trigger_condition
        })
        
    return results

@router.get("/recommendations/distribution")
async def get_recommendation_distribution(dataset_id: int = None, db: Session = Depends(get_db)):
    """
    Calculates aggregated breakdown of recommendations by category and strategy type.
    Useful for populating charts on the dashboard.
    """
    query = db.query(MitigationRecommendation).join(HotspotPrediction)
    if dataset_id:
        query = query.filter(HotspotPrediction.dataset_id == dataset_id)
        
    recs = query.all()
    categories = {}
    strategies = {}
    
    for r in recs:
        categories[r.category] = categories.get(r.category, 0) + 1
        strategies[r.strategy_name] = strategies.get(r.strategy_name, 0) + 1
        
    return {
        "categories": [{"name": k, "value": v} for k, v in categories.items()],
        "strategies": [{"name": k, "value": v} for k, v in strategies.items()]
    }

from pydantic import BaseModel
from typing import Optional

class AnalyzePointRequest(BaseModel):
    name: Optional[str] = "Selected Point"
    latitude: float
    longitude: float
    lst: float
    ndvi: float
    ndbi: float
    land_cover: Optional[str] = "Commercial"

@router.post("/recommendations/analyze")
async def analyze_custom_point(req: AnalyzePointRequest):
    """
    Runs the AI Recommendation Engine against custom coordinate readings.
    """
    hotspot_dict = {
        "name": req.name,
        "latitude": req.latitude,
        "longitude": req.longitude,
        "lst": req.lst,
        "ndvi": req.ndvi,
        "ndbi": req.ndbi,
        "land_cover": req.land_cover
    }
    
    water_coverage = 2.0
    if req.land_cover and "water" in req.land_cover.lower():
        water_coverage = 15.0
        
    recs = AIRecommendationEngine.generate_recommendations(hotspot_dict, water_body_coverage=water_coverage)
    return recs
