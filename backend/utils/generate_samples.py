import os
import json
import csv
import random
import math

SAMPLE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "samples")
os.makedirs(SAMPLE_DIR, exist_ok=True)

def generate_csv_sample():
    csv_path = os.path.join(SAMPLE_DIR, "bengaluru_sensor_readings.csv")
    headers = ["name", "latitude", "longitude", "lst", "ndvi", "ndbi", "land_cover"]
    
    # Generate 50 realistic sensor readings around Bangalore
    center_lat, center_lon = 12.9716, 77.5946
    
    bengaluru_places = [
        "Whitefield", "Electronic City", "Hebbal", "Majestic", "KR Puram", 
        "Yelahanka", "Marathahalli", "Indiranagar", "Jayanagar", "Koramangala", 
        "MG Road", "Cubbon Park", "Lalbagh", "Bannerghatta", "HSR Layout", 
        "BTM Layout", "Malleshwaram", "Rajajinagar", "Sadashivanagar", "Bellandur"
    ]
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for i in range(50):
            place_base = bengaluru_places[i % len(bengaluru_places)]
            
            # Coordinates spread around Bangalore
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(0.01, 0.08)
            lat = center_lat + dist * math.sin(angle)
            lon = center_lon + dist * math.cos(angle)
            
            # Distance from Majestic (12.9779, 77.5731) -> core builtup
            dist_from_core = ((lat - 12.9779)**2 + (lon - 77.5731)**2)**0.5
            heat_factor = max(0.0, 1.0 - (dist_from_core / 0.1))
            
            # Select land cover based on place name characteristics
            if "Park" in place_base or "Lalbagh" in place_base or "Bannerghatta" in place_base:
                land_cover = "Park"
            elif "Whitefield" in place_base or "MG Road" in place_base or "Electronic" in place_base:
                land_cover = "Commercial"
            elif "Bellandur" in place_base:
                land_cover = "Water"
            else:
                land_cover = random.choice(["Residential", "Commercial", "Industrial"])
                
            # Values based on cover
            if land_cover == "Park":
                ndvi = random.uniform(0.5, 0.8)
                ndbi = random.uniform(-0.5, -0.2)
                lst = random.uniform(22.0, 27.0) + (heat_factor * 2.0)
            elif land_cover == "Water":
                ndvi = random.uniform(-0.4, -0.1)
                ndbi = random.uniform(-0.7, -0.4)
                lst = random.uniform(19.0, 22.0)
            elif land_cover == "Industrial":
                ndvi = random.uniform(-0.15, 0.1)
                ndbi = random.uniform(0.3, 0.6)
                lst = random.uniform(39.0, 47.0) + (heat_factor * 3.5)
            elif land_cover == "Commercial":
                ndvi = random.uniform(-0.05, 0.15)
                ndbi = random.uniform(0.2, 0.45)
                lst = random.uniform(36.0, 42.0) + (heat_factor * 3.0)
            else: # Residential
                ndvi = random.uniform(0.15, 0.4)
                ndbi = random.uniform(-0.1, 0.2)
                lst = random.uniform(28.0, 35.0) + (heat_factor * 2.0)
                
            name = f"{place_base} Station #{i // len(bengaluru_places) + 1} ({land_cover})"
            writer.writerow([name, round(lat, 5), round(lon, 5), round(lst, 2), round(ndvi, 3), round(ndbi, 3), land_cover])
            
    print(f"Created Bengaluru sample CSV: {csv_path}")

def generate_geojson_sample():
    geojson_path = os.path.join(SAMPLE_DIR, "bengaluru_districts.geojson")
    
    # 5 districts around Bangalore
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
            "lst": 44.5,
            "ndvi": 0.04,
            "ndbi": 0.55,
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
            "lst": 41.8,
            "ndvi": 0.08,
            "ndbi": 0.42,
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
            "lst": 39.5,
            "ndvi": 0.12,
            "ndbi": 0.38,
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
            "lst": 26.2,
            "ndvi": 0.72,
            "ndbi": -0.32,
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
            "lst": 34.6,
            "ndvi": 0.28,
            "ndbi": 0.15,
            "type": "Residential"
        }
    ]
    
    features = []
    for d in districts:
        features.append({
            "type": "Feature",
            "properties": {
                "name": d["name"],
                "lst": d["lst"],
                "ndvi": d["ndvi"],
                "ndbi": d["ndbi"],
                "land_cover": d["type"],
                "risk_level": "Critical" if d["lst"] > 42 else "High" if d["lst"] > 35 else "Medium" if d["lst"] > 28 else "Low"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [d["coords"]]
            }
        })
        
    geojson_data = {
        "type": "FeatureCollection",
        "features": features
    }
    
    with open(geojson_path, 'w') as f:
        json.dump(geojson_data, f, indent=2)
        
    print(f"Created Bengaluru sample GeoJSON: {geojson_path}")

if __name__ == "__main__":
    generate_csv_sample()
    generate_geojson_sample()
