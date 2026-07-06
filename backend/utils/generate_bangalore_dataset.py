import os
import csv
import random
import math

SAMPLE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "samples")
os.makedirs(SAMPLE_DIR, exist_ok=True)

def generate_bangalore_complete_csv():
    csv_path = os.path.join(SAMPLE_DIR, "Bangalore_UHI_Production.csv")
    headers = ["name", "ward", "latitude", "longitude", "lst", "ndvi", "ndbi", "tree_canopy", "population_density", "land_cover"]
    
    # Bangalore center
    center_lat, center_lon = 12.9716, 77.5946
    
    # Define all 37 BBMP regions requested by the user with realistic environmental metrics
    neighborhoods = [
        {"name": "Whitefield IT Hub", "ward": "Kadugodi Ward", "lat_offset": -0.002, "lon_offset": 0.155, "base_lst": 42.8, "ndvi": 0.08, "ndbi": 0.52, "tree_canopy": 5.2, "pop_density": 14500, "cover": "Commercial"},
        {"name": "Marathahalli Junction", "ward": "Marathahalli Ward", "lat_offset": -0.018, "lon_offset": 0.105, "base_lst": 42.1, "ndvi": 0.06, "ndbi": 0.53, "tree_canopy": 4.1, "pop_density": 18200, "cover": "Commercial"},
        {"name": "Bellandur EcoSpace", "ward": "Bellandur Ward", "lat_offset": -0.039, "lon_offset": 0.078, "base_lst": 41.9, "ndvi": 0.07, "ndbi": 0.50, "tree_canopy": 6.0, "pop_density": 16800, "cover": "Commercial"},
        {"name": "Electronic City Phase 1", "ward": "Electronic City Ward", "lat_offset": -0.125, "lon_offset": 0.077, "base_lst": 42.5, "ndvi": 0.07, "ndbi": 0.49, "tree_canopy": 5.8, "pop_density": 12500, "cover": "Commercial"},
        {"name": "KR Puram Station", "ward": "KR Puram Ward", "lat_offset": 0.048, "lon_offset": 0.102, "base_lst": 41.2, "ndvi": 0.10, "ndbi": 0.44, "tree_canopy": 8.5, "pop_density": 15600, "cover": "Commercial"},
        {"name": "Hebbal Flyover Core", "ward": "Hebbal Ward", "lat_offset": 0.065, "lon_offset": -0.005, "base_lst": 39.4, "ndvi": 0.11, "ndbi": 0.40, "tree_canopy": 11.2, "pop_density": 13400, "cover": "Commercial"},
        {"name": "Yelahanka New Town", "ward": "Yelahanka Ward", "lat_offset": 0.098, "lon_offset": -0.015, "base_lst": 36.8, "ndvi": 0.20, "ndbi": 0.28, "tree_canopy": 18.4, "pop_density": 11200, "cover": "Residential"},
        {"name": "Peenya Industrial Area", "ward": "Peenya Ward", "lat_offset": 0.056, "lon_offset": -0.076, "base_lst": 45.8, "ndvi": 0.02, "ndbi": 0.65, "tree_canopy": 2.1, "pop_density": 6500, "cover": "Industrial"},
        {"name": "Rajajinagar Sector", "ward": "Rajajinagar Ward", "lat_offset": 0.025, "lon_offset": -0.045, "base_lst": 42.4, "ndvi": 0.06, "ndbi": 0.58, "tree_canopy": 4.5, "pop_density": 22400, "cover": "Industrial"},
        {"name": "Malleshwaram 18th Cross", "ward": "Malleshwaram Ward", "lat_offset": 0.032, "lon_offset": -0.028, "base_lst": 33.5, "ndvi": 0.32, "ndbi": 0.22, "tree_canopy": 31.2, "pop_density": 24800, "cover": "Residential"},
        {"name": "Sadashivanagar Canopy", "ward": "Sankey Tank Ward", "lat_offset": 0.038, "lon_offset": -0.020, "base_lst": 31.8, "ndvi": 0.44, "ndbi": 0.12, "tree_canopy": 43.5, "pop_density": 10500, "cover": "Residential"},
        {"name": "Cubbon Park Arboretum", "ward": "Sudhamanagar Ward", "lat_offset": 0.004, "lon_offset": -0.001, "base_lst": 25.8, "ndvi": 0.74, "ndbi": -0.32, "tree_canopy": 82.4, "pop_density": 250, "cover": "Park"},
        {"name": "Lalbagh Botanical Lake", "ward": "Lalbagh Ward", "lat_offset": -0.025, "lon_offset": 0.002, "base_lst": 26.4, "ndvi": 0.71, "ndbi": -0.28, "tree_canopy": 78.5, "pop_density": 300, "cover": "Park"},
        {"name": "Jayanagar 4th Block", "ward": "Jayanagar Ward", "lat_offset": -0.042, "lon_offset": -0.012, "base_lst": 32.5, "ndvi": 0.38, "ndbi": 0.16, "tree_canopy": 36.8, "pop_density": 21500, "cover": "Residential"},
        {"name": "Banashankari Temple Area", "ward": "Banashankari Ward", "lat_offset": -0.062, "lon_offset": -0.058, "base_lst": 35.1, "ndvi": 0.23, "ndbi": 0.29, "tree_canopy": 22.0, "pop_density": 23600, "cover": "Residential"},
        {"name": "Basavanagudi Heritage Sector", "ward": "Basavanagudi Ward", "lat_offset": -0.032, "lon_offset": -0.024, "base_lst": 33.2, "ndvi": 0.35, "ndbi": 0.19, "tree_canopy": 33.6, "pop_density": 25400, "cover": "Residential"},
        {"name": "Koramangala Commercial Hub", "ward": "Koramangala Ward", "lat_offset": -0.038, "lon_offset": 0.028, "base_lst": 36.4, "ndvi": 0.22, "ndbi": 0.36, "tree_canopy": 19.8, "pop_density": 21000, "cover": "Residential"},
        {"name": "Indiranagar 100ft Rd", "ward": "Indiranagar Ward", "lat_offset": 0.008, "lon_offset": 0.045, "base_lst": 37.8, "ndvi": 0.20, "ndbi": 0.38, "tree_canopy": 16.5, "pop_density": 19500, "cover": "Commercial"},
        {"name": "HSR Layout Sector 1", "ward": "HSR Layout Ward", "lat_offset": -0.062, "lon_offset": 0.052, "base_lst": 35.8, "ndvi": 0.24, "ndbi": 0.28, "tree_canopy": 21.4, "pop_density": 18500, "cover": "Residential"},
        {"name": "JP Nagar Phase 2", "ward": "JP Nagar Ward", "lat_offset": -0.065, "lon_offset": -0.018, "base_lst": 33.8, "ndvi": 0.32, "ndbi": 0.20, "tree_canopy": 29.5, "pop_density": 22800, "cover": "Residential"},
        {"name": "MG Road Business District", "ward": "Shantalanagar Ward", "lat_offset": 0.001, "lon_offset": 0.015, "base_lst": 38.6, "ndvi": 0.18, "ndbi": 0.42, "tree_canopy": 14.2, "pop_density": 16200, "cover": "Commercial"},
        {"name": "Majestic Bus Station", "ward": "Gandhinagar Ward", "lat_offset": 0.005, "lon_offset": -0.021, "base_lst": 41.2, "ndvi": 0.04, "ndbi": 0.54, "tree_canopy": 3.8, "pop_density": 28400, "cover": "Commercial"},
        {"name": "BTM Layout 2nd Stage", "ward": "BTM Layout Ward", "lat_offset": -0.055, "lon_offset": 0.020, "base_lst": 36.1, "ndvi": 0.22, "ndbi": 0.32, "tree_canopy": 20.2, "pop_density": 26500, "cover": "Residential"},
        {"name": "Sarjapur Road Corridor", "ward": "Sarjapur Ward", "lat_offset": -0.052, "lon_offset": 0.092, "base_lst": 39.5, "ndvi": 0.14, "ndbi": 0.41, "tree_canopy": 12.8, "pop_density": 14200, "cover": "Residential"},
        {"name": "Varthur Lake Buffer", "ward": "Varthur Ward", "lat_offset": -0.028, "lon_offset": 0.178, "base_lst": 29.8, "ndvi": 0.35, "ndbi": -0.15, "tree_canopy": 32.5, "pop_density": 1100, "cover": "Water"},
        {"name": "Hoodi Industrial Area", "ward": "Hoodi Ward", "lat_offset": 0.015, "lon_offset": 0.142, "base_lst": 43.5, "ndvi": 0.04, "ndbi": 0.62, "tree_canopy": 3.0, "pop_density": 7200, "cover": "Industrial"},
        {"name": "Nagavara Junction", "ward": "Nagavara Ward", "lat_offset": 0.062, "lon_offset": 0.028, "base_lst": 40.8, "ndvi": 0.12, "ndbi": 0.45, "tree_canopy": 10.4, "pop_density": 18900, "cover": "Commercial"},
        {"name": "RT Nagar Market", "ward": "RT Nagar Ward", "lat_offset": 0.049, "lon_offset": 0.002, "base_lst": 38.1, "ndvi": 0.17, "ndbi": 0.38, "tree_canopy": 14.8, "pop_density": 24200, "cover": "Residential"},
        {"name": "Kengeri Satellite Town", "ward": "Kengeri Ward", "lat_offset": -0.068, "lon_offset": -0.115, "base_lst": 36.2, "ndvi": 0.20, "ndbi": 0.30, "tree_canopy": 17.5, "pop_density": 15400, "cover": "Residential"},
        {"name": "Dasarahalli Metro Zone", "ward": "Dasarahalli Ward", "lat_offset": 0.075, "lon_offset": -0.095, "base_lst": 41.5, "ndvi": 0.10, "ndbi": 0.48, "tree_canopy": 8.0, "pop_density": 8100, "cover": "Industrial"},
        {"name": "Yeshwanthpur Rail Terminal", "ward": "Yeshwanthpur Ward", "lat_offset": 0.042, "lon_offset": -0.052, "base_lst": 42.1, "ndvi": 0.08, "ndbi": 0.50, "tree_canopy": 7.2, "pop_density": 21800, "cover": "Commercial"},
        {"name": "Domlur Tech Park", "ward": "Domlur Ward", "lat_offset": -0.008, "lon_offset": 0.041, "base_lst": 37.5, "ndvi": 0.21, "ndbi": 0.39, "tree_canopy": 18.2, "pop_density": 14100, "cover": "Commercial"},
        {"name": "Ulsoor Lake Promenade", "ward": "Ulsoor Ward", "lat_offset": 0.009, "lon_offset": 0.028, "base_lst": 27.8, "ndvi": -0.12, "ndbi": -0.40, "tree_canopy": 24.5, "pop_density": 950, "cover": "Water"},
        {"name": "Shivajinagar Market Core", "ward": "Shivajinagar Ward", "lat_offset": 0.012, "lon_offset": 0.005, "base_lst": 40.2, "ndvi": 0.06, "ndbi": 0.51, "tree_canopy": 4.8, "pop_density": 31200, "cover": "Commercial"},
        {"name": "CV Raman Nagar Complex", "ward": "CV Raman Nagar Ward", "lat_offset": 0.015, "lon_offset": 0.082, "base_lst": 36.9, "ndvi": 0.22, "ndbi": 0.33, "tree_canopy": 21.0, "pop_density": 19600, "cover": "Residential"},
        {"name": "Manyata Tech Park Core", "ward": "Manyata Ward", "lat_offset": 0.068, "lon_offset": 0.025, "base_lst": 41.2, "ndvi": 0.09, "ndbi": 0.46, "tree_canopy": 8.0, "pop_density": 13900, "cover": "Commercial"},
        {"name": "Outer Ring Road Belt", "ward": "Devarabeesanahalli Ward", "lat_offset": -0.028, "lon_offset": 0.085, "base_lst": 41.5, "ndvi": 0.08, "ndbi": 0.48, "tree_canopy": 7.5, "pop_density": 16400, "cover": "Commercial"},
    ]
    
    records = []
    
    for n in neighborhoods:
        lat = center_lat + n["lat_offset"]
        lon = center_lon + n["lon_offset"]
        
        # Primary node
        records.append([
            n["name"],
            n["ward"],
            round(lat, 5),
            round(lon, 5),
            round(n["base_lst"], 2),
            round(n["ndvi"], 3),
            round(n["ndbi"], 3),
            round(n["tree_canopy"], 2),
            n["pop_density"],
            n["cover"]
        ])
        
        # Generate 8 sub-sectors spread around the center to reach 333 points (37 * 9)
        for k in range(8):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(0.003, 0.018)
            
            sub_lat = lat + dist * math.sin(angle)
            sub_lon = lon + dist * math.cos(angle)
            
            # Dynamic variables with small variations
            lst_var = random.uniform(-2.2, 2.2)
            ndvi_var = random.uniform(-0.08, 0.08)
            ndbi_var = random.uniform(-0.07, 0.07)
            
            lst = max(18.0, min(50.0, n["base_lst"] + lst_var))
            ndvi = max(-1.0, min(1.0, n["ndvi"] + ndvi_var))
            ndbi = max(-1.0, min(1.0, n["ndbi"] + ndbi_var))
            
            # Recalculate tree canopy and pop density based on variation
            tree_canopy = max(0.0, min(100.0, n["tree_canopy"] + ndvi_var * 40.0))
            pop_density = max(100, int(n["pop_density"] + random.uniform(-1000, 1000)))
            
            cover = n["cover"]
            if ndvi > 0.45:
                cover = "Park"
                tree_canopy = max(60.0, tree_canopy)
                pop_density = max(100, int(pop_density * 0.1))
            elif ndvi < 0.0 and ndbi < 0.0:
                cover = "Water"
                tree_canopy = max(5.0, min(20.0, tree_canopy))
                pop_density = max(100, int(pop_density * 0.05))
            elif ndbi > 0.40:
                cover = "Commercial" if random.random() > 0.4 else "Industrial"
                tree_canopy = min(15.0, tree_canopy)
            elif cover == "Water" and ndvi > 0.20:
                cover = "Park"
                tree_canopy = max(50.0, tree_canopy)
                
            sub_name = f"{n['name'].replace(' Core','').replace(' IT Hub','').replace(' Station','').replace(' Core','') } Sector {chr(65+k)}"
            
            records.append([
                sub_name,
                n["ward"],
                round(sub_lat, 5),
                round(sub_lon, 5),
                round(lst, 2),
                round(ndvi, 3),
                round(ndbi, 3),
                round(tree_canopy, 2),
                pop_density,
                cover
            ])
            
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(records)
        
    print(f"Generated complete Bengaluru BBMP UHI CSV dataset with {len(records)} coordinates: {csv_path}")

if __name__ == "__main__":
    generate_bangalore_complete_csv()
