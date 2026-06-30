import os
import json
import csv
import math
import random
import numpy as np
import pandas as pd

try:
    import rasterio
    HAS_RASTERIO = True
except ImportError:
    HAS_RASTERIO = False

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

def validate_file_structure(file_path, file_type):
    """
    Synchronously validates that the file structure contains the required geospatial
    and climatic metrics. Raises ValueError if validation fails.
    """
    if file_type == "csv":
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            raise ValueError(f"Invalid CSV file format: {str(e)}")
            
        columns = [c.lower().strip() for c in df.columns]
        
        # Check Latitude mapping
        has_lat = any(any(pat in c for pat in ['lat', 'latitude', 'coord_y']) for c in columns)
        if not has_lat:
            raise ValueError("Geospatial validation failed: Missing required latitude coordinate column ('lat' or 'latitude').")
            
        # Check Longitude mapping
        has_lon = any(any(pat in c for pat in ['lon', 'lng', 'longitude', 'coord_x']) for c in columns)
        if not has_lon:
            raise ValueError("Geospatial validation failed: Missing required longitude coordinate column ('lon', 'lng', or 'longitude').")
            
        # Check Temperature mapping
        has_temp = any(any(pat in c for pat in ['lst', 'temp', 'temperature', 'heat']) for c in columns)
        if not has_temp:
            raise ValueError("Climatic validation failed: Missing required temperature column ('lst', 'temp', or 'temperature').")

    elif file_type == "geojson":
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
        except Exception as e:
            raise ValueError(f"Invalid GeoJSON JSON structure: {str(e)}")
            
        if not isinstance(data, dict) or "features" not in data:
            raise ValueError("GeoJSON validation failed: File must contain a top-level 'features' array collection.")
            
        features = data.get("features", [])
        if not features:
            raise ValueError("GeoJSON validation failed: Features array is empty.")
            
        # Inspect first feature properties for validation
        first_feat = features[0]
        geom = first_feat.get("geometry", {})
        props = first_feat.get("properties", {})
        
        if not geom or "type" not in geom:
            raise ValueError("GeoJSON validation failed: Feature is missing structural geometry.")
            
        # Check property temperature columns
        prop_keys = [k.lower().strip() for k in props.keys()]
        has_temp = any(any(pat in k for pat in ['lst', 'temp', 'temperature']) for k in prop_keys)
        if not has_temp:
            raise ValueError("Climatic validation failed: GeoJSON feature properties must contain temperature details ('lst' or 'temp').")

    elif file_type in ["tif", "tiff", "geotiff"]:
        if not HAS_RASTERIO:
            # If rasterio is missing, we check if it is a valid binary image file using PIL
            if HAS_PIL:
                try:
                    with Image.open(file_path) as img:
                        img.verify()
                except Exception as e:
                    raise ValueError(f"TIFF validation failed: Image file is corrupted or unreadable. {str(e)}")
            return
            
        try:
            with rasterio.open(file_path) as src:
                if src.count < 1:
                    raise ValueError("TIFF validation failed: Raster band count must be at least 1.")
        except Exception as e:
            raise ValueError(f"TIFF validation failed: Could not parse raster spatial metadata. {str(e)}")

def process_uploaded_file(file_path, file_type):
    """
    Parses various file types and returns a list of standardized spatial points.
    """
    records = []
    
    if file_type == "csv":
        records = _process_csv(file_path)
    elif file_type == "geojson":
        records = _process_geojson(file_path)
    elif file_type in ["tif", "tiff", "geotiff"]:
        records = _process_tiff(file_path)
    elif file_type in ["png", "jpg", "jpeg"]:
        records = _process_image(file_path)
    else:
        records = generate_synthetic_data(50)
        
    cleaned_records = []
    for i, r in enumerate(records):
        lat = float(r.get("latitude", 12.9716))
        lon = float(r.get("longitude", 77.5946))
        lst = float(r.get("lst", random.uniform(22.0, 48.0)))
        ndvi = float(r.get("ndvi", random.uniform(-0.2, 0.8)))
        ndbi = float(r.get("ndbi", random.uniform(-0.5, 0.6)))
        
        built_up_density = float(r.get("built_up_density", max(0.0, min(100.0, (ndbi + 1) * 50.0))))
        vegetation_density = float(r.get("vegetation_density", max(0.0, min(100.0, (ndvi + 1) * 50.0))))
        
        land_cover = r.get("land_cover")
        if not land_cover:
            if ndvi > 0.4:
                land_cover = "Park" if random.random() > 0.3 else "Forest"
            elif ndbi > 0.2:
                land_cover = "Industrial" if random.random() > 0.6 else "Commercial"
            elif lst > 38.0 and ndvi < 0.1:
                land_cover = "Commercial" if random.random() > 0.5 else "Industrial"
            else:
                land_cover = "Residential"
                
        name = r.get("name", f"Hotspot Sector #{i+1} ({land_cover})")
        
        cleaned_records.append({
            "name": name,
            "latitude": round(lat, 6),
            "longitude": round(lon, 6),
            "lst": round(lst, 2),
            "ndvi": round(ndvi, 3),
            "ndbi": round(ndbi, 3),
            "built_up_density": round(built_up_density, 1),
            "vegetation_density": round(vegetation_density, 1),
            "land_cover": land_cover
        })
        
    return cleaned_records

def _process_csv(file_path):
    records = []
    df = pd.read_csv(file_path)
    
    # Dynamic Column Mapping Heuristics
    col_map = {}
    for col in df.columns:
        c_low = col.lower().strip()
        if any(pat in c_low for pat in ['latitude', 'lat', 'coord_y']):
            col_map['latitude'] = col
        elif any(pat in c_low for pat in ['longitude', 'lon', 'lng', 'coord_x']):
            col_map['longitude'] = col
        elif any(pat in c_low for pat in ['lst', 'temp', 'temperature', 'heat']):
            col_map['lst'] = col
        elif 'ndvi' in c_low:
            col_map['ndvi'] = col
        elif 'ndbi' in c_low:
            col_map['ndbi'] = col
        elif any(pat in c_low for pat in ['cover', 'land_cover', 'type']):
            col_map['land_cover'] = col
        elif any(pat in c_low for pat in ['name', 'station', 'label']):
            col_map['name'] = col
            
    for _, row in df.iterrows():
        record = {}
        for target_k, source_k in col_map.items():
            val = row[source_k]
            # Convert NaN values
            if pd.isna(val):
                continue
            record[target_k] = val
        records.append(record)
        
    return records

def _process_geojson(file_path):
    records = []
    with open(file_path, 'r') as f:
        data = json.load(f)
        
    features = data.get("features", [])
    for i, feat in enumerate(features):
        props = feat.get("properties", {})
        geom = feat.get("geometry", {})
        
        lat, lon = None, None
        geom_type = geom.get("type", "").lower()
        coords = geom.get("coordinates", [])
        
        if geom_type == "point":
            lon, lat = coords[0], coords[1]
        elif geom_type in ["polygon", "multipolygon"]:
            if geom_type == "polygon":
                poly_coords = coords[0]
            else:
                poly_coords = coords[0][0]
            
            lons = [c[0] for c in poly_coords if isinstance(c, list) and len(c) >= 2]
            lats = [c[1] for c in poly_coords if isinstance(c, list) and len(c) >= 2]
            if lats and lons:
                lat = sum(lats) / len(lats)
                lon = sum(lons) / len(lons)
        
        if lat is not None and lon is not None:
            # Map dynamic temperature properties
            temp_val = None
            for tk in ["lst", "temp", "temperature"]:
                for pk in props.keys():
                    if tk in pk.lower():
                        temp_val = props[pk]
                        break
                if temp_val is not None:
                    break

            # Map land cover properties
            cover_val = None
            for ck in ["cover", "land_cover", "type"]:
                for pk in props.keys():
                    if ck in pk.lower():
                        cover_val = props[pk]
                        break
                if cover_val is not None:
                    break

            # Map name properties
            name_val = props.get("name", props.get("district", f"GeoZone #{i+1}"))

            record = {
                "latitude": lat,
                "longitude": lon,
                "name": name_val,
                "lst": temp_val,
                "ndvi": props.get("ndvi"),
                "ndbi": props.get("ndbi"),
                "land_cover": cover_val
            }
            record = {k: v for k, v in record.items() if v is not None}
            records.append(record)
            
    return records

def _process_tiff(file_path):
    records = []
    if HAS_RASTERIO:
        try:
            with rasterio.open(file_path) as src:
                h, w = src.height, src.width
                step_y = max(1, h // 10)
                step_x = max(1, w // 10)
                band1 = src.read(1)
                
                for r in range(0, h, step_y):
                    for c in range(0, w, step_x):
                        lon, lat = src.xy(r, c)
                        val = float(band1[r, c])
                        norm_val = val / 255.0 if band1.max() > 1.0 else val
                        
                        lst = 20.0 + norm_val * 25.0
                        ndvi = -0.2 + norm_val * 1.0
                        ndbi = 0.5 - norm_val * 0.9
                        
                        records.append({
                            "latitude": lat,
                            "longitude": lon,
                            "lst": lst,
                            "ndvi": ndvi,
                            "ndbi": ndbi,
                        })
                return records
        except Exception:
            pass
            
    return _process_image(file_path)

def _process_image(file_path):
    records = []
    if not HAS_PIL:
        return generate_synthetic_data(50)
        
    try:
        with Image.open(file_path) as img:
            img_rgb = img.convert("RGB")
            w, h = img_rgb.size
            center_lat, center_lon = 12.9716, 77.5946
            
            step_x = max(1, w // 10)
            step_y = max(1, h // 10)
            
            for y in range(0, h, step_y):
                for x in range(0, w, step_x):
                    r, g, b = img_rgb.getpixel((x, y))
                    g_ratio = g / (r + g + b + 1e-5)
                    r_ratio = r / (r + g + b + 1e-5)
                    brightness = (r + g + b) / 765.0
                    
                    ndvi = -0.2 + g_ratio * 1.8 if g > r else -0.3 + (g_ratio * 0.8)
                    ndvi = max(-1.0, min(1.0, ndvi))
                    
                    ndbi = -0.5 + r_ratio * 1.5 if r > g else -0.6 + (r_ratio * 0.9)
                    ndbi = max(-1.0, min(1.0, ndbi))
                    
                    lst = 25.0 + (brightness * 20.0) - (ndvi * 8.0)
                    
                    lat = center_lat + ((h/2 - y) / h) * 0.08
                    lon = center_lon + ((x - w/2) / w) * 0.12
                    
                    records.append({
                        "latitude": lat,
                        "longitude": lon,
                        "lst": lst,
                        "ndvi": ndvi,
                        "ndbi": ndbi
                    })
    except Exception:
        return generate_synthetic_data(50)
        
    return records

def generate_synthetic_data(count=50, center_lat=12.9716, center_lon=77.5946, radius=0.08):
    records = []
    land_covers = ["Residential", "Commercial", "Industrial", "Park", "Water"]
    bengaluru_places = [
        "Whitefield", "Electronic City", "Hebbal", "Majestic", "KR Puram", 
        "Yelahanka", "Marathahalli", "Indiranagar", "Jayanagar", "Koramangala", 
        "MG Road", "Cubbon Park", "Lalbagh", "Bannerghatta", "HSR Layout", 
        "BTM Layout", "Malleshwaram", "Rajajinagar", "Sadashivanagar", "Bellandur"
    ]
    
    for i in range(count):
        angle = random.uniform(0, 2 * math.pi)
        r = random.uniform(0, radius)
        lat = center_lat + r * math.sin(angle)
        lon = center_lon + r * math.cos(angle)
        
        dist_factor = 1.0 - (r / radius)  
        if dist_factor > 0.7:
            land_cover = random.choice(["Commercial", "Industrial", "Residential"])
        elif dist_factor > 0.4:
            land_cover = random.choice(["Residential", "Commercial", "Park"])
        else:
            land_cover = random.choice(["Residential", "Park", "Water"])
            
        if land_cover == "Park":
            ndvi = random.uniform(0.5, 0.85)
            ndbi = random.uniform(-0.6, -0.2)
            lst = random.uniform(22.0, 28.0) + (dist_factor * 2.0)
        elif land_cover == "Water":
            ndvi = random.uniform(-0.5, -0.1)
            ndbi = random.uniform(-0.8, -0.5)
            lst = random.uniform(19.0, 23.0)
        elif land_cover == "Industrial":
            ndvi = random.uniform(-0.15, 0.1)
            ndbi = random.uniform(0.3, 0.65)
            lst = random.uniform(38.0, 48.0) + (dist_factor * 4.0)
        elif land_cover == "Commercial":
            ndvi = random.uniform(0.0, 0.2)
            ndbi = random.uniform(0.2, 0.5)
            lst = random.uniform(35.0, 43.0) + (dist_factor * 3.0)
        else:
            ndvi = random.uniform(0.15, 0.45)
            ndbi = random.uniform(-0.1, 0.25)
            lst = random.uniform(28.0, 36.0) + (dist_factor * 2.0)
            
        place_base = bengaluru_places[i % len(bengaluru_places)]
        name = f"{place_base} Sector {i // len(bengaluru_places) + 1} ({land_cover})"
        
        records.append({
            "name": name,
            "latitude": lat,
            "longitude": lon,
            "lst": lst,
            "ndvi": ndvi,
            "ndbi": ndbi,
            "land_cover": land_cover
        })
        
    return records
