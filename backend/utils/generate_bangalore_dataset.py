import os
import csv
import random
import math

SAMPLE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "samples")
os.makedirs(SAMPLE_DIR, exist_ok=True)

def generate_bangalore_complete_csv():
    csv_path = os.path.join(SAMPLE_DIR, "bangalore_complete_uhi.csv")
    headers = ["name", "latitude", "longitude", "lst", "ndvi", "ndbi", "land_cover"]
    
    # Bangalore center
    center_lat, center_lon = 12.9716, 77.5946
    
    # Neighborhoods config: Name, relative offset from center, base temperature, vegetation density, builtup density, land cover
    neighborhoods = [
        # Central Hubs
        {"name": "Majestic Bus Terminus", "lat_offset": 0.005, "lon_offset": -0.021, "base_lst": 41.2, "ndvi": 0.04, "ndbi": 0.54, "cover": "Commercial"},
        {"name": "MG Road Metro Hub", "lat_offset": 0.001, "lon_offset": 0.015, "base_lst": 38.6, "ndvi": 0.18, "ndbi": 0.42, "cover": "Commercial"},
        {"name": "Indiranagar 100ft Rd", "lat_offset": 0.008, "lon_offset": 0.045, "base_lst": 36.4, "ndvi": 0.22, "ndbi": 0.36, "cover": "Commercial"},
        
        # Industrial Heat Sources (North & West)
        {"name": "Peenya Phase 1 Industrial Yard", "lat_offset": 0.056, "lon_offset": -0.076, "base_lst": 45.8, "ndvi": 0.02, "ndbi": 0.65, "cover": "Industrial"},
        {"name": "Peenya Phase 2 Assembly Plant", "lat_offset": 0.061, "lon_offset": -0.082, "base_lst": 46.5, "ndvi": 0.01, "ndbi": 0.68, "cover": "Industrial"},
        {"name": "Rajajinagar Industrial Town", "lat_offset": 0.025, "lon_offset": -0.045, "base_lst": 42.4, "ndvi": 0.06, "ndbi": 0.58, "cover": "Industrial"},
        {"name": "Nayandahalli Fabrications", "lat_offset": -0.025, "lon_offset": -0.065, "base_lst": 43.1, "ndvi": 0.05, "ndbi": 0.60, "cover": "Industrial"},
        
        # IT Corridor & Rapid Expansion (East)
        {"name": "Whitefield IT Export Zone", "lat_offset": -0.002, "lon_offset": 0.155, "base_lst": 42.8, "ndvi": 0.08, "ndbi": 0.52, "cover": "Commercial"},
        {"name": "Kadugodi Logistics Park", "lat_offset": 0.025, "lon_offset": 0.165, "base_lst": 44.2, "ndvi": 0.05, "ndbi": 0.59, "cover": "Industrial"},
        {"name": "Mahadevapura IT Corridor", "lat_offset": 0.021, "lon_offset": 0.102, "base_lst": 41.5, "ndvi": 0.09, "ndbi": 0.48, "cover": "Commercial"},
        {"name": "Marathahalli Bridge junction", "lat_offset": -0.018, "lon_offset": 0.105, "base_lst": 42.1, "ndvi": 0.06, "ndbi": 0.53, "cover": "Commercial"},
        {"name": "Bellandur EcoSpace IT Park", "lat_offset": -0.041, "lon_offset": 0.082, "base_lst": 41.9, "ndvi": 0.07, "ndbi": 0.50, "cover": "Commercial"},
        
        # High Density Residential (South & West)
        {"name": "Koramangala 3rd Block", "lat_offset": -0.038, "lon_offset": 0.028, "base_lst": 34.2, "ndvi": 0.28, "ndbi": 0.22, "cover": "Residential"},
        {"name": "HSR Layout Sector 1", "lat_offset": -0.062, "lon_offset": 0.052, "base_lst": 35.8, "ndvi": 0.24, "ndbi": 0.28, "cover": "Residential"},
        {"name": "Jayanagar 4th Block", "lat_offset": -0.042, "lon_offset": -0.012, "base_lst": 32.5, "ndvi": 0.38, "ndbi": 0.16, "cover": "Residential"},
        {"name": "JP Nagar Phase 2", "lat_offset": -0.065, "lon_offset": -0.018, "base_lst": 33.8, "ndvi": 0.32, "ndbi": 0.20, "cover": "Residential"},
        {"name": "Kengeri Satellite Town", "lat_offset": -0.068, "lon_offset": -0.115, "base_lst": 36.2, "ndvi": 0.20, "ndbi": 0.30, "cover": "Residential"},
        {"name": "Vijayanagar Core Wards", "lat_offset": 0.005, "lon_offset": -0.058, "base_lst": 35.1, "ndvi": 0.22, "ndbi": 0.26, "cover": "Residential"},
        
        # Green Buffers & Lakes (Cooling Zones)
        {"name": "IISc Campus Botanical Buffer", "lat_offset": 0.043, "lon_offset": -0.032, "base_lst": 27.2, "ndvi": 0.65, "ndbi": -0.15, "cover": "Park"},
        {"name": "Cubbon Park Arboretum", "lat_offset": 0.004, "lon_offset": -0.001, "base_lst": 25.8, "ndvi": 0.74, "ndbi": -0.32, "cover": "Park"},
        {"name": "Lalbagh Lake Sanctuary", "lat_offset": -0.025, "lon_offset": 0.002, "base_lst": 26.4, "ndvi": 0.71, "ndbi": -0.28, "cover": "Park"},
        {"name": "Bellandur Lake Basin", "lat_offset": -0.039, "lon_offset": 0.078, "base_lst": 28.5, "ndvi": -0.15, "ndbi": -0.45, "cover": "Water"},
        {"name": "Ulsoor Lake Water Body", "lat_offset": 0.009, "lon_offset": 0.028, "base_lst": 27.8, "ndvi": -0.12, "ndbi": -0.40, "cover": "Water"},
        {"name": "Hebbal Lake Sanctuary", "lat_offset": 0.065, "lon_offset": -0.005, "base_lst": 28.1, "ndvi": 0.42, "ndbi": -0.20, "cover": "Water"},
        
        # Yelahanka & North Expansion
        {"name": "Yelahanka New Town", "lat_offset": 0.098, "lon_offset": -0.015, "base_lst": 36.8, "ndvi": 0.20, "ndbi": 0.28, "cover": "Residential"},
        {"name": "Hebbal Flyover Junction", "lat_offset": 0.055, "lon_offset": -0.008, "base_lst": 39.4, "ndvi": 0.11, "ndbi": 0.40, "cover": "Commercial"},
        {"name": "Manyata Tech Park Core", "lat_offset": 0.058, "lon_offset": 0.022, "base_lst": 41.2, "ndvi": 0.09, "ndbi": 0.46, "cover": "Commercial"},
    ]
    
    # We will generate 120 points by sampling around these neighborhoods
    records = []
    
    for n in neighborhoods:
        # Generate the main location
        lat = center_lat + n["lat_offset"]
        lon = center_lon + n["lon_offset"]
        
        records.append([
            n["name"],
            round(lat, 5),
            round(lon, 5),
            round(n["base_lst"], 2),
            round(n["ndvi"], 3),
            round(n["ndbi"], 3),
            n["cover"]
        ])
        
        # Generate 3-4 spatial dispersion points around each neighborhood
        for k in range(random.randint(3, 5)):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(0.003, 0.015) # spread radius
            
            d_lat = lat + dist * math.sin(angle)
            d_lon = lon + dist * math.cos(angle)
            
            # Add small random variation to index values
            lst_var = random.uniform(-1.5, 1.5)
            ndvi_var = random.uniform(-0.06, 0.06)
            ndbi_var = random.uniform(-0.05, 0.05)
            
            lst = max(18.0, min(50.0, n["base_lst"] + lst_var))
            ndvi = max(-1.0, min(1.0, n["ndvi"] + ndvi_var))
            ndbi = max(-1.0, min(1.0, n["ndbi"] + ndbi_var))
            
            # Auto-assign cover type to vary a bit
            cover = n["cover"]
            if ndvi > 0.45:
                cover = "Park"
            elif ndbi > 0.35:
                cover = "Commercial" if random.random() > 0.3 else "Industrial"
            
            sub_name = f"{n['name'].split(' ')[0]} Sector {chr(65+k)}"
            
            records.append([
                sub_name,
                round(d_lat, 5),
                round(d_lon, 5),
                round(lst, 2),
                round(ndvi, 3),
                round(ndbi, 3),
                cover
            ])
            
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(records)
        
    print(f"Created complete Bangalore spatial CSV dataset with {len(records)} coordinates: {csv_path}")

if __name__ == "__main__":
    generate_bangalore_complete_csv()
