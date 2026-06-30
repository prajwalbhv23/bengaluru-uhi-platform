import random
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import UploadDataset, HotspotPrediction

router = APIRouter(prefix="/api")

@router.get("/map/hotspots")
async def get_map_hotspots(dataset_id: int = None, db: Session = Depends(get_db)):
    """
    Returns spatial coordinate records of hotspots.
    Includes popup details (temp, NDVI, risk level, priority suggestions).
    """
    if dataset_id:
        dataset = db.query(UploadDataset).filter(UploadDataset.id == dataset_id).first()
    else:
        dataset = db.query(UploadDataset).filter(UploadDataset.status == "Processed").order_by(UploadDataset.upload_time.desc()).first()
        
    if not dataset:
        # Fallback synthetic hotspots around NYC for the default sample view
        return get_mock_hotspots()
        
    hotspots = db.query(HotspotPrediction).filter(HotspotPrediction.dataset_id == dataset.id).all()
    if not hotspots:
        return get_mock_hotspots()
        
    results = []
    for h in hotspots:
        top_sug = [r.strategy_name for r in h.recommendations[:2]]
        results.append({
            "id": h.id,
            "name": h.name,
            "latitude": h.latitude,
            "longitude": h.longitude,
            "lst": h.lst,
            "ndvi": h.ndvi,
            "ndbi": h.ndbi,
            "risk_score": h.risk_score,
            "risk_level": h.risk_level,
            "land_cover": h.land_cover,
            "growth_5yr": h.growth_prediction,
            "top_suggestions": top_sug
        })
        
    return results

@router.get("/map/districts")
async def get_district_geojson(dataset_id: int = None, db: Session = Depends(get_db)):
    """
    Generates a GeoJSON FeatureCollection representing urban districts.
    Allows React-Leaflet to paint choropleth layers.
    """
    is_bangalore = True
    
    # Resolve active dataset coordinates to toggle between NYC and Bangalore maps
    if dataset_id:
        h = db.query(HotspotPrediction).filter(HotspotPrediction.dataset_id == dataset_id).first()
        if h and 12.0 < h.latitude < 14.0 and 76.5 < h.longitude < 78.5:
            is_bangalore = True
    else:
        dataset = db.query(UploadDataset).filter(UploadDataset.status == "Processed").order_by(UploadDataset.upload_time.desc()).first()
        if dataset:
            h = db.query(HotspotPrediction).filter(HotspotPrediction.dataset_id == dataset.id).first()
            if h and 12.0 < h.latitude < 14.0 and 76.5 < h.longitude < 78.5:
                is_bangalore = True
                
    if is_bangalore:
        districts = [
            {
                "name": "Peenya Sector (North-West)",
                "coords": [
                    [77.49, 13.01],
                    [77.54, 13.05],
                    [77.53, 13.01],
                    [77.50, 12.99],
                    [77.49, 13.01]
                ],
                "base_temp": 44.5,
                "base_ndvi": 0.04,
                "type": "Industrial"
            },
            {
                "name": "Whitefield Corridor (East)",
                "coords": [
                    [77.72, 12.94],
                    [77.78, 12.98],
                    [77.76, 12.93],
                    [77.73, 12.92],
                    [77.72, 12.94]
                ],
                "base_temp": 41.8,
                "base_ndvi": 0.08,
                "type": "Commercial"
            },
            {
                "name": "Majestic Core (Central)",
                "coords": [
                    [77.56, 12.96],
                    [77.59, 12.98],
                    [77.58, 12.95],
                    [77.55, 12.94],
                    [77.56, 12.96]
                ],
                "base_temp": 39.5,
                "base_ndvi": 0.12,
                "type": "Commercial"
            },
            {
                "name": "Cubbon / Lalbagh Canopy",
                "coords": [
                    [77.585, 12.962],
                    [77.605, 12.982],
                    [77.595, 12.952],
                    [77.575, 12.942],
                    [77.585, 12.962]
                ],
                "base_temp": 26.2,
                "base_ndvi": 0.72,
                "type": "Park"
            },
            {
                "name": "HSR / Koramangala (South)",
                "coords": [
                    [77.61, 12.91],
                    [77.66, 12.94],
                    [77.64, 12.90],
                    [77.62, 12.89],
                    [77.61, 12.91]
                ],
                "base_temp": 34.6,
                "base_ndvi": 0.28,
                "type": "Residential"
            }
        ]
    else:
        districts = [
            {
                "name": "District 1 (Downtown)",
                "center": [40.708, -74.006],
                "coords": [
                    [-74.015, 40.702],
                    [-74.010, 40.718],
                    [-73.998, 40.715],
                    [-74.005, 40.700],
                    [-74.015, 40.702]
                ],
                "base_temp": 39.5,
                "base_ndvi": 0.12,
                "type": "Commercial"
            },
            {
                "name": "District 2 (Midtown East)",
                "center": [40.755, -73.975],
                "coords": [
                    [-73.985, 40.748],
                    [-73.980, 40.765],
                    [-73.965, 40.760],
                    [-73.972, 40.742],
                    [-73.985, 40.748]
                ],
                "base_temp": 42.8,
                "base_ndvi": 0.08,
                "type": "Industrial"
            },
            {
                "name": "District 3 (West Side)",
                "center": [40.760, -73.998],
                "coords": [
                    [-74.008, 40.750],
                    [-74.000, 40.772],
                    [-73.988, 40.768],
                    [-73.995, 40.745],
                    [-74.008, 40.750]
                ],
                "base_temp": 34.6,
                "base_ndvi": 0.22,
                "type": "Residential"
            },
            {
                "name": "District 4 (Central Park East)",
                "center": [40.785, -73.962],
                "coords": [
                    [-73.972, 40.772],
                    [-73.962, 40.795],
                    [-73.950, 40.790],
                    [-73.960, 40.767],
                    [-73.972, 40.772]
                ],
                "base_temp": 25.8,
                "base_ndvi": 0.68,
                "type": "Park"
            },
            {
                "name": "District 5 (Queens West)",
                "center": [40.744, -73.955],
                "coords": [
                    [-73.962, 40.738],
                    [-73.958, 40.755],
                    [-73.940, 40.750],
                    [-73.945, 40.732],
                    [-73.962, 40.738]
                ],
                "base_temp": 37.2,
                "base_ndvi": 0.18,
                "type": "Residential"
            }
        ]
        
    features = []
    for d in districts:
        # Convert coords to GeoJSON coordinate style [lng, lat]
        polygon_coords = [d["coords"]]
        
        # Check if database has live coordinates in this region to adjust LST
        features.append({
            "type": "Feature",
            "properties": {
                "name": d["name"],
                "lst": d["base_temp"],
                "ndvi": d["base_ndvi"],
                "land_cover": d["type"],
                "risk_level": "Critical" if d["base_temp"] > 40 else "High" if d["base_temp"] > 35 else "Medium" if d["base_temp"] > 28 else "Low",
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": polygon_coords
            }
        })
        
    return {
        "type": "FeatureCollection",
        "features": features
    }

def get_mock_hotspots():
    """
    Returns synthetic hotspots representing the Bengaluru UHI grid.
    """
    mock_spots = [
        {"name": "Peenya Phase 1 Industrial Yard", "lat": 13.0285, "lon": 77.5186, "lst": 45.8, "ndvi": 0.02, "ndbi": 0.65, "cover": "Industrial", "sug": ["Cool Roof Coatings", "Perimeter Miyawaki Buffers"]},
        {"name": "Whitefield IT Export Zone", "lat": 12.9698, "lon": 77.7500, "lst": 42.8, "ndvi": 0.08, "ndbi": 0.52, "cover": "Commercial", "sug": ["Commercial Roof Gardens", "PV Shaded Parking Canopies"]},
        {"name": "Majestic Bus Terminus Core", "lat": 12.9779, "lon": 77.5731, "lst": 41.2, "ndvi": 0.04, "ndbi": 0.54, "cover": "Commercial", "sug": ["Permeable Cool Pavements", "Vertical Green Walls"]},
        {"name": "Silk Board Junction Plaza", "lat": 12.9176, "lon": 77.6234, "lst": 43.5, "ndvi": 0.03, "ndbi": 0.58, "cover": "Commercial", "sug": ["PV Shaded Parking Canopies", "Cool Pavements"]},
        {"name": "Electronic City IT Corridor", "lat": 12.8465, "lon": 77.6722, "lst": 42.1, "ndvi": 0.07, "ndbi": 0.50, "cover": "Commercial", "sug": ["Green Corridors", "Cool Roof Coatings"]},
        {"name": "Outer Ring Road (ORR) Highway", "lat": 12.9279, "lon": 77.6808, "lst": 40.8, "ndvi": 0.06, "ndbi": 0.53, "cover": "Commercial", "sug": ["Tree Canopy Enhancement", "Permeable Cool Pavements"]},
        {"name": "Hebbal Flyover Junction", "lat": 13.0355, "lon": 77.5981, "lst": 39.4, "ndvi": 0.11, "ndbi": 0.40, "cover": "Commercial", "sug": ["Urban Forestry", "Permeable Walkways"]},
        {"name": "Koramangala Commercial Sector", "lat": 12.9352, "lon": 77.6244, "lst": 36.4, "ndvi": 0.22, "ndbi": 0.36, "cover": "Residential", "sug": ["Community Pocket Parks", "Street Trees"]},
        {"name": "Jayanagar Ward Canopy", "lat": 12.9299, "lon": 77.5824, "lst": 32.5, "ndvi": 0.38, "ndbi": 0.16, "cover": "Residential", "sug": ["Residential Tree Canopy", "Community Shared Gardens"]},
        {"name": "Cubbon Park Arboretum Buffer", "lat": 12.9720, "lon": 77.5940, "lst": 25.8, "ndvi": 0.74, "ndbi": -0.32, "cover": "Park", "sug": ["Native Grassland Planting", "Water Retaining Bioswales"]},
        {"name": "Lalbagh Lake Wetlands", "lat": 12.9452, "lon": 77.5902, "lst": 26.4, "ndvi": 0.71, "ndbi": -0.28, "cover": "Park", "sug": ["Wetland Restoration", "Native Grassland Planting"]},
        {"name": "Bellandur Lake Buffer Area", "lat": 12.9304, "lon": 77.6784, "lst": 28.5, "ndvi": -0.15, "ndbi": -0.45, "cover": "Water", "sug": ["Wetland Restoration", "Water Body Hydrological Restoration"]},
    ]
    
    results = []
    for i, s in enumerate(mock_spots):
        risk_score = min(100.0, max(0.0, (s["lst"] - 20.0) / 28.0 * 100.0))
        results.append({
            "id": i + 1000,
            "name": s["name"],
            "latitude": s["lat"],
            "longitude": s["lon"],
            "lst": s["lst"],
            "ndvi": s["ndvi"],
            "ndbi": s["ndbi"],
            "risk_score": round(risk_score, 1),
            "risk_level": "Critical" if s["lst"] > 42.0 else "High" if s["lst"] > 35.0 else "Medium" if s["lst"] > 28.0 else "Low",
            "land_cover": s["cover"],
            "growth_5yr": round((s["ndbi"] - s["ndvi"]) * 1.2 + 0.8, 2),
            "top_suggestions": s["sug"]
        })
    return results
