from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import UploadDataset, HotspotPrediction, MitigationRecommendation

router = APIRouter(prefix="/api")

@router.get("/dashboard/summary")
async def get_dashboard_summary(dataset_id: int = None, db: Session = Depends(get_db)):
    """
    Computes summary KPI indicators and trend series for charts.
    Supports filtering by specific dataset_id; defaults to latest processed.
    """
    # 1. Resolve dataset
    if dataset_id:
        dataset = db.query(UploadDataset).filter(UploadDataset.id == dataset_id).first()
    else:
        dataset = db.query(UploadDataset).filter(UploadDataset.status == "Processed").order_by(UploadDataset.upload_time.desc()).first()
        
    if not dataset:
        raise HTTPException(status_code=404, detail="No active processed dataset found. Please load the digital twin dataset.")
        
    hotspots = db.query(HotspotPrediction).filter(HotspotPrediction.dataset_id == dataset.id).all()
    if not hotspots:
        raise HTTPException(status_code=404, detail="No hotspots found for this dataset.")
        
    # Aggregate stats
    lst_vals = [h.lst for h in hotspots]
    ndvi_vals = [h.ndvi for h in hotspots]
    ndbi_vals = [h.ndbi for h in hotspots]
    
    avg_temp = sum(lst_vals) / len(lst_vals)
    max_temp = max(lst_vals)
    min_temp = min(lst_vals)
    avg_ndvi = sum(ndvi_vals) / len(ndvi_vals)
    avg_ndbi = sum(ndbi_vals) / len(ndbi_vals)
    
    hotspots_found = len(hotspots)
    high_risk_zones = sum(1 for h in hotspots if h.risk_level in ["High", "Critical"])
    
    # Calculate carbon reduction and projects
    recs = db.query(MitigationRecommendation).join(HotspotPrediction).filter(HotspotPrediction.dataset_id == dataset.id).all()
    mitigation_projects = len(recs)
    carbon_reduction_est = sum(r.carbon_reduction for r in recs)
    
    # Land cover breakdown
    land_cover_counts = {}
    for h in hotspots:
        lc = h.land_cover or "Unknown"
        land_cover_counts[lc] = land_cover_counts.get(lc, 0) + 1
        
    land_cover_data = [{"name": k, "value": v} for k, v in land_cover_counts.items()]
    
    # Risk levels breakdown
    risk_counts = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
    for h in hotspots:
        risk_counts[h.risk_level] = risk_counts.get(h.risk_level, 0) + 1
        
    risk_data = [{"name": k, "value": v} for k, v in risk_counts.items()]
    
    # Sort hotspots by temperature to show a trend / distribution chart (take 30 representative points for clean rendering)
    sorted_by_temp = sorted(hotspots, key=lambda x: x.lst)
    step = max(1, len(sorted_by_temp) // 30)
    sampled_hotspots = sorted_by_temp[::step][:30]
    
    temp_trend = [{"name": h.name.split(" ")[0] if " " in h.name else h.name, "temp": h.lst, "ndvi": h.ndvi} for h in sampled_hotspots]
    
    return {
        "dataset_info": {
            "id": dataset.id,
            "filename": dataset.filename,
            "file_type": dataset.file_type,
            "upload_time": dataset.upload_time.isoformat(),
            "mitigation_summary": dataset.mitigation_summary
        },
        "kpis": {
            "avg_temp": round(avg_temp, 1),
            "max_temp": round(max_temp, 1),
            "avg_ndvi": round(avg_ndvi, 3),
            "avg_ndbi": round(avg_ndbi, 3),
            "hotspots_found": hotspots_found,
            "high_risk_zones": high_risk_zones,
            "mitigation_projects": mitigation_projects,
            "carbon_reduction": round(carbon_reduction_est, 1),
            "uhi_intensity": round(dataset.heat_island_intensity or (max_temp - min_temp), 1),
            "water_body_coverage": round(dataset.water_body_coverage or (sum(1 for h in hotspots if h.land_cover.lower() == 'water') / len(hotspots) * 100 if hotspots else 0.0), 1)
        },
        "charts": {
            "land_cover": land_cover_data,
            "risk_levels": risk_data,
            "temp_trend": temp_trend
        }
    }
