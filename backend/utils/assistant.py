import re
import random

class AIAssistant:
    def __init__(self, db_session=None):
        self.db = db_session
        
    def answer_question(self, question, session_id="default", selected_location=None):
        """
        Processes a natural language query and replies with domain-specific knowledge
        and contextual insights derived from current database statistics.
        """
        q = question.lower().strip()
        
        # 1. Fetch current dataset context if possible
        stats = self._get_current_dataset_stats()
        
        # Contextual location analysis override
        if selected_location and any(w in q for w in ["here", "this location", "this hotspot", "why is it hot", "mitigation", "do here", "this point"]):
            loc_name = selected_location.get("name", "the selected location")
            loc_temp = selected_location.get("lst", 0.0)
            loc_ndvi = selected_location.get("ndvi", 0.0)
            loc_ndbi = selected_location.get("ndbi", 0.0)
            loc_cover = selected_location.get("land_cover", "Commercial")
            
            if loc_ndvi < 0.20 and loc_ndbi > 0.45:
                cause = "concrete built-up sink absorption with minimal vegetation cover"
            elif loc_ndvi < 0.20:
                cause = "severe lack of tree canopies and green corridors"
            elif loc_ndbi > 0.45:
                cause = "superheated dark asphalt and concrete roads"
            else:
                cause = "localized sensible heat storage"
                
            return (
                f"### Custom Climate Analysis: {loc_name}\n\n"
                f"**Current Readings**: Surface Temperature (LST) is **{loc_temp:.1f}°C**, vegetation density (NDVI) is **{loc_ndvi:.3f}**, and built-up index (NDBI) is **{loc_ndbi:.3f}**.\n\n"
                f"**Primary Heat Driver**: The heat island intensity at this spot is driven by **{cause}**.\n\n"
                f"**AI Recommended Core Action**: For {loc_name}, we recommend applying **Cool Roof Coatings** (which can reduce surface temperatures by up to 4.5°C) and establishing **Miyawaki Forest Buffers** or **street tree canopies** to expand evapotranspiration cooling."
            )
        
        # 2. Match intent keywords
        # Bangalore specific queries
        if "hottest" in q and ("bengaluru" in q or "bangalore" in q):
            return (
                "Based on climate intelligence data for Bengaluru, the hottest zones are concentrated around the eastern IT corridors "
                "and north-western heavy industrial zones:\n\n"
                "1. **Peenya Industrial Area**: Reaches peak LST of **45.8°C to 46.5°C** due to massive concentrations of sheet metal roofing, asphalt yards, and low green cover.\n"
                "2. **Whitefield IT Export Zone**: Peaks at **42.8°C** as a result of extensive concrete build-up, glazed facades, and vehicular heat accumulation.\n"
                "3. **Silk Board Junction**: Reaches **43.5°C** due to dense gridlock thermal emissions and massive paved surface areas."
            )
        elif "whitefield" in q:
            return (
                "For **Whitefield**, the AI Recommendation Engine prescribes the following key adaptation strategies:\n\n"
                "1. **Cool Roof Retrofitting**: Apply reflective coatings to wide flat concrete roofs on tech campuses to decrease indoor heat loads by up to 5°C.\n"
                "2. **Rooftop Green Gardens**: Convert flat rooftops to intensive vegetated gardens to provide evapo-cooling.\n"
                "3. **Photovoltaic Parking Canopies**: Shade large corporate parking lots with solar panel arrays to prevent pavement heat absorption while generating clean electricity."
            )
        elif "electronic city" in q and ("cubbon" in q or "park" in q):
            return (
                "**Electronic City is significantly warmer than Cubbon Park (by up to 16.3°C)** due to the contrast in their environmental indices:\n\n"
                "* **Electronic City**: Has a high NDBI (Built-up index) of **0.50** and a low NDVI (Vegetation index) of **0.07**. The massive concentration of asphalt roads and concrete campuses act as a heat sink, trapping solar heat.\n"
                "* **Cubbon Park**: Features a high NDVI of **0.74** and negative NDBI of **-0.32**. Its dense forest canopy blocks solar rays from hitting the soil and releases moisture via **evapotranspiration**, cooling the surrounding air by several degrees."
            )
            
        # UHI / Hotspot Danger
        elif any(w in q for w in ["dangerous", "danger", "hazard", "consequence", "impact", "threat"]):
            return self._get_danger_response(stats)
            
        # What should the city do / mitigation
        elif any(w in q for w in ["what should the city do", "what to do", "mitigation", "strategy", "solutions", "action plan"]):
            return self._get_action_response(stats)
            
        # Trees cooling impact
        elif any(w in q for w in ["tree", "forest", "planting", "canopy", "vegetation", "cooling"]):
            return self._get_tree_response()
            
        # NDVI / NDBI importance
        elif "ndvi" in q:
            return self._get_ndvi_response()
        elif "ndbi" in q:
            return self._get_ndbi_response()
            
        # Statistics of current dashboard
        elif any(w in q for w in ["hotspot count", "how many hotspots", "statistics", "dataset info", "max temp", "highest temperature"]):
            return self._get_stats_response(stats)
            
        # Cost or budget queries
        elif any(w in q for w in ["cost", "budget", "expensive", "cheapest", "price", "funding"]):
            return self._get_cost_response(stats)
            
        # Default / Fallback response
        else:
            return self._get_fallback_response(stats)

    def _get_current_dataset_stats(self):
        """
        Retrieves summary metrics from the DB to provide real-time context.
        """
        stats = {
            "has_data": False,
            "filename": "No active dataset",
            "hotspot_count": 0,
            "max_lst": 0.0,
            "avg_lst": 0.0,
            "avg_ndvi": 0.0,
            "critical_count": 0,
            "high_count": 0,
        }
        
        if not self.db:
            return stats
            
        try:
            from models import UploadDataset, HotspotPrediction
            # Get latest processed dataset
            dataset = self.db.query(UploadDataset).filter(UploadDataset.status == "Processed").order_by(UploadDataset.upload_time.desc()).first()
            if dataset:
                stats["has_data"] = True
                stats["filename"] = dataset.filename
                
                hotspots = self.db.query(HotspotPrediction).filter(HotspotPrediction.dataset_id == dataset.id).all()
                if hotspots:
                    stats["hotspot_count"] = len(hotspots)
                    stats["max_lst"] = max(h.lst for h in hotspots)
                    stats["avg_lst"] = sum(h.lst for h in hotspots) / len(hotspots)
                    stats["avg_ndvi"] = sum(h.ndvi for h in hotspots) / len(hotspots)
                    stats["critical_count"] = sum(1 for h in hotspots if h.risk_level == "Critical")
                    stats["high_count"] = sum(1 for h in hotspots if h.risk_level == "High")
        except Exception as e:
            print(f"Error fetching assistant context: {e}")
            
        return stats

    def _get_danger_response(self, stats):
        header = ""
        if stats["has_data"] and stats["hotspot_count"] > 0:
            header = f"Analyzing your uploaded dataset **{stats['filename']}**, we detected **{stats['hotspot_count']} hotspots** with a peak temperature of **{stats['max_lst']:.1f}°C**.\n\n"
            
        return (
            f"{header}Urban Heat Island (UHI) hotspots are dangerous for several reasons:\n"
            "1. **Public Health Risks**: Extreme heat is a leading cause of weather-related deaths. It triggers heat exhaustion, heat stroke, and exacerbates cardiovascular and respiratory illnesses, especially among vulnerable groups like children and the elderly.\n"
            "2. **Grid Strain**: Hotspots spike building cooling demands, causing power surges and potential blackouts during peak hours.\n"
            "3. **Environmental Degradation**: Increased temperatures accelerate chemical reactions in the atmosphere, raising ground-level ozone production (smog) and deteriorating air quality.\n"
            "4. **Water Quality**: Stormwater running off superheated asphalt carries thermal pollution into streams and rivers, disrupting aquatic ecosystems."
        )

    def _get_action_response(self, stats):
        if stats["has_data"] and stats["hotspot_count"] > 0:
            rec_text = ""
            if stats["critical_count"] > 0:
                rec_text = f"Priority should be given to the **{stats['critical_count']} Critical zones** (temp > 42°C). For these core areas, a multi-tier intervention is required: deploying **High-Albedo Reflective Roof Coatings** immediately to reduce solar gain, and initiating a **Miyawaki Urban Forestry** program to provide physical shade. "
            else:
                rec_text = f"With an average hotspot temperature of **{stats['avg_lst']:.1f}°C**, the city should focus on mid-scale interventions. "
                
            return (
                f"Based on the analysis of **{stats['filename']}**, here is the recommended action plan:\n\n"
                f"* **Immediate Response**: {rec_text}\n"
                f"* **Commercial Zones**: Scale up **Vertical Green Walls** and **Photovoltaic Parking Canopies** which provide shade while producing renewable energy.\n"
                f"* **Residential Areas**: Launch a community-led **Tree Canopy Program** targeting streets with low NDVI. Distributing native shade trees can reduce surface temperatures by up to 4°C in residential neighborhoods.\n"
                f"* **Industrial Sectors**: Mandate **Perimeter Green Buffers** and light-colored pavements to block thermal radiation from leaving industrial yards."
            )
        else:
            return (
                "To mitigate Urban Heat Islands, cities should implement a three-pillared strategy:\n"
                "1. **Green Infrastructure**: Planting street trees, pocket parks, and green roofs to maximize evapotranspiration.\n"
                "2. **Cool Materials**: Applying cool roofing coatings and retrofitting asphalt roads with high-albedo permeable cool pavements.\n"
                "3. **Smart Urban Design**: Structuring buildings to allow ventilation corridors and using water bodies (bioswales, retention ponds) as cooling buffers."
            )

    def _get_tree_response(self):
        return (
            "Trees are the most cost-effective tool in UHI mitigation. Their cooling capacity relies on two primary mechanisms:\n\n"
            "1. **Evapotranspiration**: Trees absorb water through roots and release it as vapor from leaves. This process cools the air by converting sensible heat (air temp) into latent heat. **A single healthy tree can provide cooling equivalent to 10 room-sized air conditioners operating 20 hours a day.**\n"
            "2. **Shading**: Tree canopies block solar radiation from reaching the ground, keeping surfaces up to **11°C to 25°C cooler** compared to unshaded pavement.\n\n"
            "Overall, urban forests can lower ambient air temperatures by **2.0°C to 5.5°C** depending on canopy density, species selection, and distribution."
        )

    def _get_ndvi_response(self):
        return (
            "**NDVI (Normalized Difference Vegetation Index)** is a critical metric in UHI analysis.\n\n"
            "* **Definition**: It measures the density and health of vegetation by comparing visible red light (absorbed by chlorophyll) and near-infrared light (reflected by leaf structure):\n"
            "  `NDVI = (NIR - Red) / (NIR + Red)`\n"
            "* **Scale**: It ranges from **-1.0 to +1.0**. Negative values represent water or snow, values close to 0 represent concrete, soil, or built-up surfaces, and values > 0.4 represent dense green vegetation.\n"
            "* **UHI Correlation**: NDVI shares a strong inverse relationship with surface temperature. As NDVI decreases (loss of vegetation), Land Surface Temperature (LST) rises. The dashboard monitors NDVI to locate thermal weaknesses where parklands and street trees should be added."
        )

    def _get_ndbi_response(self):
        return (
            "**NDBI (Normalized Difference Built-up Index)** is used to map impervious surfaces and concrete built-up areas.\n\n"
            "* **Definition**: It isolates built-up infrastructure by comparing shortwave infrared (SWIR) and near-infrared (NIR) light:\n"
            "  `NDBI = (SWIR - NIR) / (SWIR + NIR)`\n"
            "* **Scale**: It ranges from **-1.0 to +1.0**. Higher positive values correspond to dense asphalt, concrete buildings, and roads.\n"
            "* **UHI Correlation**: NDBI is directly proportional to temperature. High NDBI areas behave as heat sinks, storing heat during the day and radiating it at night. Minimizing NDBI impacts requires retrofitting roofs and replacing impermeable concrete with cool permeable pavements."
        )

    def _get_stats_response(self, stats):
        if not stats["has_data"]:
            return "There is currently no active dataset uploaded. Please upload a GeoTIFF, CSV, or GeoJSON dataset in the **Upload Dataset** panel to analyze local heat index details."
            
        return (
            f"### Active Dataset Analytics Summary\n"
            f"* **Source File**: `{stats['filename']}`\n"
            f"* **Total Hotspots Found**: **{stats['hotspot_count']} locations**\n"
            f"* **Peak Temperature (LST)**: **{stats['max_lst']:.2f}°C**\n"
            f"* **Average Hotspot Temp**: **{stats['avg_lst']:.2f}°C**\n"
            f"* **Average Vegetation Index (NDVI)**: **{stats['avg_ndvi']:.3f}**\n"
            f"* **Risk Distribution**: **{stats['critical_count']} Critical**, **{stats['high_count']} High**, and **{stats['hotspot_count'] - stats['critical_count'] - stats['high_count']} Moderate/Low** risk zones.\n\n"
            f"You can view the full geographical mapping of these zones on the interactive dashboard."
        )

    def _get_cost_response(self, stats):
        return (
            "Mitigation strategy costs vary based on implementation scale and structural requirements:\n\n"
            "1. **Low Cost ($10 - $25 per m²)**: *Reflective Cool Roof coatings* and *Native Grassland planting* are the most economical, offering fast returns on investment.\n"
            "2. **Moderate Cost ($25 - $75 per m²)**: *Permeable Cool Pavements*, *Residential Tree planting*, and *Community Pocket Parks*.\n"
            "3. **High Cost ($80 - $250+ per m²)**: *Commercial Roof Gardens* and modular *Vertical Living Walls*. These require structural reinforcement, irrigation, and higher maintenance, but deliver massive energy offsets and aesthetics.\n\n"
            "Our recommendation engine estimates costs automatically for each hotspot, sorting by cost-efficiency to help cities optimize tight budgets."
        )

    def _get_fallback_response(self, stats):
        return (
            "I am your Bengaluru AI Climate Intelligence Assistant. I can help you analyze Urban Heat Islands (UHI) and plan green cooling strategies.\n\n"
            "Here are some questions you can ask me:\n"
            "* *What are the hottest regions in Bengaluru?*\n"
            "* *Suggest mitigation strategies for Whitefield.*\n"
            "* *Why is Electronic City warmer than Cubbon Park?*\n"
            "* *Why is this hotspot dangerous?*\n"
            "* *What should the city do?*\n"
            "* *How much temperature can trees reduce?*\n"
            "* *What are the stats of the current dataset?*"
        )
