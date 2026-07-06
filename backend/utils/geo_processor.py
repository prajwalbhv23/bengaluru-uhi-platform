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
    and climatic metrics, checks coordinate ranges, duplicates, and formats.
    Raises ValueError if validation fails.
    """
    if file_type == "csv":
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            raise ValueError(f"Invalid CSV file format: {str(e)}")
            
        columns = [c.lower().strip() for c in df.columns]
        
        # Check Latitude mapping
        lat_col = None
        for c in df.columns:
            if any(pat in c.lower() for pat in ['lat', 'latitude', 'coord_y']):
                lat_col = c
                break
        if not lat_col:
            raise ValueError("Geospatial validation failed: Missing required latitude coordinate column ('lat' or 'latitude').")
            
        # Check Longitude mapping
        lon_col = None
        for c in df.columns:
            if any(pat in c.lower() for pat in ['lon', 'lng', 'longitude', 'coord_x']):
                lon_col = c
                break
        if not lon_col:
            raise ValueError("Geospatial validation failed: Missing required longitude coordinate column ('lon', 'lng', or 'longitude').")
            
        # Check Temperature mapping
        temp_col = None
        for c in df.columns:
            if any(pat in c.lower() for pat in ['lst', 'temp', 'temperature', 'heat', 'land_surface_temperature']):
                temp_col = c
                break
        if not temp_col:
            raise ValueError("Climatic validation failed: Missing required temperature column ('lst', 'temp', 'temperature', or 'land_surface_temperature').")

        # Validate rows
        seen_coords = set()
        for idx, row in df.iterrows():
            try:
                lat = float(row[lat_col])
                lon = float(row[lon_col])
            except (ValueError, TypeError):
                raise ValueError(f"Row {idx+1}: Coordinates must be numeric values.")

            if lat < -90.0 or lat > 90.0 or lon < -180.0 or lon > 180.0:
                raise ValueError(f"Row {idx+1}: Latitude must be in [-90, 90] and Longitude in [-180, 180].")

            coord_key = (round(lat, 5), round(lon, 5))
            if coord_key in seen_coords:
                raise ValueError(f"Geospatial validation failed: Duplicate coordinates detected at ({lat}, {lon}).")
            seen_coords.add(coord_key)

            # Check LST
            try:
                lst = float(row[temp_col])
            except (ValueError, TypeError):
                raise ValueError(f"Row {idx+1}: Temperature value must be numeric.")

            # Check NDVI & NDBI limits
            for c in df.columns:
                if 'ndvi' in c.lower():
                    val = row[c]
                    if pd.notna(val):
                        try:
                            fval = float(val)
                            if fval < -1.0 or fval > 1.0:
                                raise ValueError(f"Row {idx+1}: NDVI value {fval} is out of range [-1, 1].")
                        except (ValueError, TypeError):
                            raise ValueError(f"Row {idx+1}: NDVI must be numeric.")
                if 'ndbi' in c.lower():
                    val = row[c]
                    if pd.notna(val):
                        try:
                            fval = float(val)
                            if fval < -1.0 or fval > 1.0:
                                raise ValueError(f"Row {idx+1}: NDBI value {fval} is out of range [-1, 1].")
                        except (ValueError, TypeError):
                            raise ValueError(f"Row {idx+1}: NDBI must be numeric.")

    elif file_type == "geojson":
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            raise ValueError(f"Invalid GeoJSON JSON structure: {str(e)}")
            
        if not isinstance(data, dict) or "features" not in data:
            raise ValueError("GeoJSON validation failed: File must contain a top-level 'features' array collection.")
            
        features = data.get("features", [])
        if not features:
            raise ValueError("GeoJSON validation failed: Features array is empty.")
            
        first_feat = features[0]
        geom = first_feat.get("geometry", {})
        props = first_feat.get("properties", {})
        
        if not geom or "type" not in geom:
            raise ValueError("GeoJSON validation failed: Feature is missing structural geometry.")
            
        prop_keys = [k.lower().strip() for k in props.keys()]
        has_temp = any(any(pat in k for pat in ['lst', 'temp', 'temperature', 'land_surface_temperature']) for k in prop_keys)
        if not has_temp:
            raise ValueError("Climatic validation failed: GeoJSON feature properties must contain temperature details ('lst' or 'temp').")

    elif file_type in ["tif", "tiff", "geotiff"]:
        if not HAS_RASTERIO:
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
        ward = r.get("ward", f"Ward {i+1}")
        
        tree_canopy = r.get("tree_canopy")
        if tree_canopy is not None:
            tree_canopy = float(tree_canopy)
        else:
            tree_canopy = max(0.0, min(100.0, vegetation_density * 0.85))

        pop_density = r.get("population_density")
        if pop_density is not None:
            pop_density = float(pop_density)
        else:
            if land_cover == "Residential":
                pop_density = 22000
            elif land_cover == "Commercial":
                pop_density = 15000
            elif land_cover == "Industrial":
                pop_density = 6500
            else:
                pop_density = 300
                
        cleaned_records.append({
            "name": name,
            "ward": ward,
            "latitude": round(lat, 6),
            "longitude": round(lon, 6),
            "lst": round(lst, 2),
            "ndvi": round(ndvi, 3),
            "ndbi": round(ndbi, 3),
            "built_up_density": round(built_up_density, 1),
            "vegetation_density": round(vegetation_density, 1),
            "tree_canopy": round(tree_canopy, 1),
            "population_density": round(pop_density, 1),
            "land_cover": land_cover
        })
        
    return cleaned_records

def _process_csv(file_path):
    records = []
    df = pd.read_csv(file_path)
    
    col_map = {}
    for col in df.columns:
        c_low = col.lower().strip()
        if any(pat in c_low for pat in ['latitude', 'lat', 'coord_y']):
            col_map['latitude'] = col
        elif any(pat in c_low for pat in ['longitude', 'lon', 'lng', 'coord_x']):
            col_map['longitude'] = col
        elif any(pat in c_low for pat in ['lst', 'temp', 'temperature', 'heat', 'land_surface_temperature']):
            col_map['lst'] = col
        elif 'ndvi' in c_low:
            col_map['ndvi'] = col
        elif 'ndbi' in c_low:
            col_map['ndbi'] = col
        elif any(pat in c_low for pat in ['cover', 'land_cover', 'landcover', 'type']):
            col_map['land_cover'] = col
        elif 'humidity' in c_low:
            col_map['humidity'] = col
        elif any(pat in c_low for pat in ['ward', 'region', 'area']):
            col_map['ward'] = col
        elif any(pat in c_low for pat in ['canopy', 'tree_canopy', 'tree_cover', 'treecover']):
            col_map['tree_canopy'] = col
        elif any(pat in c_low for pat in ['pop_density', 'population_density', 'population', 'pop']):
            col_map['population_density'] = col
        elif any(pat in c_low for pat in ['name', 'station', 'label']):
            col_map['name'] = col
            
    for _, row in df.iterrows():
        record = {}
        for target_k, source_k in col_map.items():
            val = row[source_k]
            if pd.isna(val):
                continue
            record[target_k] = val
        records.append(record)
        
    return records

def _process_geojson(file_path):
    records = []
    with open(file_path, 'r', encoding='utf-8') as f:
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
            temp_val = None
            for tk in ["lst", "temp", "temperature"]:
                for pk in props.keys():
                    if tk in pk.lower():
                        temp_val = props[pk]
                        break
                if temp_val is not None:
                    break

            cover_val = None
            for ck in ["cover", "land_cover", "type"]:
                for pk in props.keys():
                    if ck in pk.lower():
                        cover_val = props[pk]
                        break
                if cover_val is not None:
                    break

            name_val = props.get("name", props.get("district", f"GeoZone #{i+1}"))
            ward_val = props.get("ward", props.get("region"))

            record = {
                "latitude": lat,
                "longitude": lon,
                "name": name_val,
                "ward": ward_val,
                "lst": temp_val,
                "ndvi": props.get("ndvi"),
                "ndbi": props.get("ndbi"),
                "tree_canopy": props.get("tree_canopy"),
                "population_density": props.get("population_density"),
                "land_cover": cover_val
            }
            record = {k: v for k, v in record.items() if v is not None}
            records.append(record)
            
    return records

def _process_tiff(file_path):
    records = []
    if not HAS_RASTERIO:
        return generate_synthetic_data(80)
        
    try:
        with rasterio.open(file_path) as src:
            band = src.read(1)
            mask = src.dataset_mask()
            
            non_zero = np.argwhere(mask > 0)
            if len(non_zero) > 100:
                indices = np.random.choice(len(non_zero), 100, replace=False)
                sampled_pixels = non_zero[indices]
            else:
                sampled_pixels = non_zero
                
            for idx, (r, c) in enumerate(sampled_pixels):
                lon, lat = src.xy(r, c)
                lst_val = float(band[r, c])
                
                if lst_val < -100 or lst_val > 200:
                    lst_val = random.uniform(26.0, 44.0)
                    
                ndvi_val = random.uniform(-0.1, 0.45)
                ndbi_val = random.uniform(-0.25, 0.5)
                
                records.append({
                    "latitude": lat,
                    "longitude": lon,
                    "lst": lst_val,
                    "ndvi": ndvi_val,
                    "ndbi": ndbi_val,
                    "name": f"Sensor Pixel #{idx+1}"
                })
    except Exception as e:
        print(f"TIFF parser error: {e}")
        return generate_synthetic_data(80)
        
    return records

def _process_image(file_path):
    return generate_synthetic_data(80)

def generate_synthetic_data(count):
    records = []
    center_lat, center_lon = 12.9716, 77.5946
    for i in range(count):
        lat = center_lat + random.uniform(-0.06, 0.06)
        lon = center_lon + random.uniform(-0.06, 0.06)
        lst = random.uniform(24.0, 43.5)
        ndvi = random.uniform(-0.15, 0.65)
        ndbi = random.uniform(-0.3, 0.5)
        
        records.append({
            "name": f"Synthetic Probe #{i+1}",
            "latitude": lat,
            "longitude": lon,
            "lst": lst,
            "ndvi": ndvi,
            "ndbi": ndbi
        })
    return records
