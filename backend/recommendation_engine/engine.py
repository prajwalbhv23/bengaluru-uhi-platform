class AIRecommendationEngine:
    @staticmethod
    def generate_recommendations(hotspot, water_body_coverage=2.0):
        """
        Overhauled GIS Decision Support Rule-Based Inference Engine.
        Generates distinct mitigation plans based on location cover type, LST, NDVI, NDBI, and risk level.
        Healthy regions receive preservation-focused actions; high-risk regions receive aggressive interventions.
        """
        lst = hotspot.get("lst", 30.0)
        ndvi = hotspot.get("ndvi", 0.2)
        ndbi = hotspot.get("ndbi", 0.2)
        land_cover = hotspot.get("land_cover", "Residential").lower()
        place_name = hotspot.get("name", "Selected Location")
        risk_level = hotspot.get("risk_level", "Moderate")
        
        # Calculate local humidity and heat index proxy
        humidity = max(15, min(95, round(40 + ndvi * 50)))
        heat_index = lst - 3.5 + (humidity * 0.05)
        
        recommendations = []
        
        # ----------------------------------------------------
        # CASE 8 & CASE 3: Risk == LOW or Healthy Forest Regions (e.g. Cubbon Park, Lalbagh)
        is_healthy = risk_level.upper() == "LOW" or (ndvi > 0.70 and lst < 30.0)
        
        if is_healthy:
            # Preservation-focused recommendations ONLY. Do NOT recommend tree plantation, green corridors, or urban forestry.
            return [
                {
                    "strategy_name": "Preserve Existing Vegetation Canopy",
                    "category": "Green Infrastructure",
                    "reason": "Current environmental conditions are healthy. Preserves active shading and prevents future urban encroachment.",
                    "trigger_condition": f"NDVI = {ndvi:.2f} (>0.70), LST = {lst:.1f}°C (<30°C)",
                    "technical_explanation": "Existing multi-layered vegetation canopy absorbs over 85% of incoming solar radiation, shielding underlying soils.",
                    "recommended_implementation": "Restrict tree clearance permits, establish structural preservation buffers, and inspect canopy health quarterly.",
                    "priority_level": "Long Term",
                    "temp_reduction": 0.0,
                    "cost_level": "Low",
                    "implementation_time": "Continuous",
                    "environmental_benefits": "Preserved tree shade,Protected local wildlife,Maintained soil carbon levels",
                    "sustainability_benefits": "SDG 15: Life on Land. Protects existing botanical assets.",
                    "confidence_score": 98.0,
                    "severity": "Low"
                },
                {
                    "strategy_name": "Maintain Local Biodiversity",
                    "category": "Green Infrastructure",
                    "reason": "Preserves native species richness to maintain microclimate stability.",
                    "trigger_condition": f"NDVI = {ndvi:.2f} (>0.70), Risk = {risk_level}",
                    "technical_explanation": "Diverse plant species create resilient root and leaf systems that withstand dry spells, maintaining constant evapotranspiration.",
                    "recommended_implementation": "Conduct botanical audits, remove invasive weeds, and introduce native forest ground cover plants.",
                    "priority_level": "Long Term",
                    "temp_reduction": 0.0,
                    "cost_level": "Low",
                    "implementation_time": "Continuous",
                    "environmental_benefits": "Eco-balance maintenance,Protected flora and fauna,Natural air filtration",
                    "sustainability_benefits": "SDG 15: Life on Land",
                    "confidence_score": 97.0,
                    "severity": "Low"
                },
                {
                    "strategy_name": "Protect Green Space and Canopy",
                    "category": "Policy / Urban Planning",
                    "reason": "Ensures the location is legally protected against commercial urban conversion.",
                    "trigger_condition": f"LST = {lst:.1f}°C, NDBI = {ndbi:.2f} (<0.15)",
                    "technical_explanation": "Strict municipal zoning codes prevent impervious building paving, locking in local thermal sinks.",
                    "recommended_implementation": "Enforce municipal zoning status of park boundaries and install perimeter fence controls.",
                    "priority_level": "Long Term",
                    "temp_reduction": 0.0,
                    "cost_level": "Low",
                    "implementation_time": "Continuous",
                    "environmental_benefits": "Encroachment protection,Maintained urban cooling corridors",
                    "sustainability_benefits": "SDG 11: Sustainable Cities",
                    "confidence_score": 95.0,
                    "severity": "Low"
                },
                {
                    "strategy_name": "Prevent Illegal Land Conversion",
                    "category": "Policy / Urban Planning",
                    "reason": "Prevents encroachment from paving the healthy vegetative buffer zones.",
                    "trigger_condition": f"NDBI = {ndbi:.2f} (<0.15), NDVI = {ndvi:.2f}",
                    "technical_explanation": "Protects soils from asphalt capping, maintaining natural moisture absorption grids.",
                    "recommended_implementation": "Deploy monthly satellite NDVI anomaly scans to detect unauthorized structural changes.",
                    "priority_level": "Long Term",
                    "temp_reduction": 0.0,
                    "cost_level": "Low",
                    "implementation_time": "Continuous",
                    "environmental_benefits": "Soil porosity conservation,Intact ground infiltration",
                    "sustainability_benefits": "SDG 15: Life on Land",
                    "confidence_score": 96.0,
                    "severity": "Low"
                },
                {
                    "strategy_name": "Improve Irrigation During Dry Months",
                    "category": "Green Infrastructure",
                    "reason": "Ensures existing trees maintain optimal transpiration during hot summer spells.",
                    "trigger_condition": f"Humidity = {humidity}%, NDVI = {ndvi:.2f}",
                    "technical_explanation": "Supplemental root watering prevents plant stress, keeping leaf transpiration active during peak heatwaves.",
                    "recommended_implementation": "Install low-loss micro-irrigation using local treated greywater reserves.",
                    "priority_level": "Long Term",
                    "temp_reduction": 0.2,
                    "cost_level": "Low",
                    "implementation_time": "3-6 months",
                    "environmental_benefits": "Protected canopy health,Maintained transpiration levels",
                    "sustainability_benefits": "SDG 6: Clean Water & Sanitation",
                    "confidence_score": 94.0,
                    "severity": "Low"
                },
                {
                    "strategy_name": "Continuous Environmental Monitoring",
                    "category": "Policy / Urban Planning",
                    "reason": "Ensures that seasonal variations do not initiate localized warming trends.",
                    "trigger_condition": f"LST = {lst:.1f}°C, NDVI = {ndvi:.2f}",
                    "technical_explanation": "Telemetry records baseline LST parameters, giving early alerts on thermal rises.",
                    "recommended_implementation": "Deploy low-cost temperature and humidity IoT nodes across a 200-meter grid.",
                    "priority_level": "Long Term",
                    "temp_reduction": 0.0,
                    "cost_level": "Low",
                    "implementation_time": "1-2 months",
                    "environmental_benefits": "Early heat rise detection,Accurate spatial trend modeling",
                    "sustainability_benefits": "SDG 11: Sustainable Cities",
                    "confidence_score": 96.0,
                    "severity": "Low"
                }
            ]

        # ----------------------------------------------------
        # CASE 7: Lakes or Wetlands (e.g. Bellandur Lake, Varthur Lake)
        is_water = "lake" in place_name.lower() or "wetland" in place_name.lower() or land_cover == "water"
        if is_water:
            # Water-focused recommendations ONLY. Do NOT recommend tree plantation everywhere.
            return [
                {
                    "strategy_name": "Wetland Conservation & De-silting",
                    "category": "Green Infrastructure",
                    "reason": "Clears sludge to maximize open water capacity and maintain evaporative cooling buffers.",
                    "trigger_condition": f"Land Cover = Water, Water coverage = {water_body_coverage:.1f}%",
                    "technical_explanation": "Removing organic silt increases the water column depth, reducing bottom absorption and convective heat release.",
                    "recommended_implementation": "Deploy suction dredgers to remove toxic sludge and redirect untreated industrial sewage.",
                    "priority_level": "Immediate" if lst > 35.0 else "Short Term",
                    "temp_reduction": 2.5,
                    "cost_level": "High",
                    "implementation_time": "12-24 months",
                    "environmental_benefits": "Maximized evaporative cooling,Restored native biodiversity,Increased water capacity",
                    "sustainability_benefits": "SDG 6: Clean Water. Recharges regional aquifers and filters contaminants.",
                    "confidence_score": 94.0,
                    "severity": "High"
                },
                {
                    "strategy_name": "Buffer Vegetation Restoration",
                    "category": "Green Infrastructure",
                    "reason": "Controls shore sensible heat and stops soil erosion into the water bed.",
                    "trigger_condition": f"Land Cover = Water, NDVI = {ndvi:.2f}",
                    "technical_explanation": "A dense ring of reeds and grasses shades perimeter soils, cooling hot winds passing over the lake.",
                    "recommended_implementation": "Plant native reeds (Typha angustifolia) and marsh grasses along a 15-meter bank margin.",
                    "priority_level": "Short Term",
                    "temp_reduction": 1.8,
                    "cost_level": "Medium",
                    "implementation_time": "6-12 months",
                    "environmental_benefits": "Shoreline soil cooling,Restored riparian habitats,Reduced lakeside erosion",
                    "sustainability_benefits": "SDG 15: Life on Land",
                    "confidence_score": 93.0,
                    "severity": "Moderate"
                },
                {
                    "strategy_name": "Water Quality Monitoring Telemetry",
                    "category": "Policy / Urban Planning",
                    "reason": "Tracks thermal shifts and prevents heat-absorbing algal blooms.",
                    "trigger_condition": f"Land Cover = Water, LST = {lst:.1f}°C",
                    "technical_explanation": "Algae absorb solar radiation at the water surface, heating the lake. Clean water maintains a higher thermal inertia.",
                    "recommended_implementation": "Install solar-powered floating telemetry buoys transmitting DO, temperature, and pH logs.",
                    "priority_level": "Short Term",
                    "temp_reduction": 0.5,
                    "cost_level": "Low",
                    "implementation_time": "3-6 months",
                    "environmental_benefits": "Early detection of algal blooms,Clean water heat buffering",
                    "sustainability_benefits": "SDG 6: Clean Water & Sanitation",
                    "confidence_score": 90.0,
                    "severity": "Moderate"
                },
                {
                    "strategy_name": "Shoreline Wetland Restoration",
                    "category": "Green Infrastructure",
                    "reason": "Replaces hard concrete lake banks with natural vegetation to absorb heat.",
                    "trigger_condition": f"Land Cover = Water, NDBI = {ndbi:.2f}",
                    "technical_explanation": "Porous earth banks retain water moisture, keeping shoreline temperatures lower than concrete retaining walls.",
                    "recommended_implementation": "Remove vertical concrete retaining walls and construct stone geogrids seeded with marsh grass.",
                    "priority_level": "Long Term",
                    "temp_reduction": 1.2,
                    "cost_level": "High",
                    "implementation_time": "12-24 months",
                    "environmental_benefits": "Lakeside thermal cooling,Filtered runoff filtration,Recharged local aquifers",
                    "sustainability_benefits": "SDG 11: Sustainable Cities",
                    "confidence_score": 91.0,
                    "severity": "Moderate"
                }
            ]

        # ----------------------------------------------------
        # CASE 1: Critical Hotspots (LST > 40°C AND NDVI < 0.20 AND NDBI > 0.55)
        is_critical_hotspot = lst > 40.0 and ndvi < 0.20 and ndbi > 0.55
        if is_critical_hotspot:
            # Generate aggressive mitigation strategies
            recommendations.extend([
                {
                    "strategy_name": "Urban Tree Plantation",
                    "category": "Green Infrastructure",
                    "reason": "Aggressive greening to shade concrete surfaces and reduce critical heat load.",
                    "trigger_condition": f"LST = {lst:.1f}°C (>40°C), NDVI = {ndvi:.2f} (<0.20), NDBI = {ndbi:.2f} (>0.55)",
                    "technical_explanation": "Tree leaves block solar radiation from heating concrete, and evaporate water to cool the air, converting sensible heat into latent heat.",
                    "recommended_implementation": "Plant high-density street trees such as Neem and Honge at 5-meter intervals on pedestrian paths.",
                    "priority_level": "Immediate",
                    "temp_reduction": 3.2,
                    "cost_level": "Medium",
                    "implementation_time": "6-12 months",
                    "environmental_benefits": "Lower surface temperature,Better air quality,Carbon sequestration,Reduced stormwater runoff",
                    "sustainability_benefits": "SDG 11: Sustainable Cities. Promotes local microclimatic thermal comfort.",
                    "confidence_score": 96.0,
                    "severity": "Critical"
                },
                {
                    "strategy_name": "Green Corridors",
                    "category": "Green Infrastructure",
                    "reason": "Establishes continuous vegetative pathways to promote wind ventilation.",
                    "trigger_condition": f"LST = {lst:.1f}°C (>40°C), NDVI = {ndvi:.2f} (<0.20), NDBI = {ndbi:.2f} (>0.55)",
                    "technical_explanation": "Linear forest zones create active wind passages, sweeping stagnant hot air out of urban canyons.",
                    "recommended_implementation": "Acquire easement plots to link local parks with a 15-meter-wide vegetated trail.",
                    "priority_level": "Immediate",
                    "temp_reduction": 2.8,
                    "cost_level": "High",
                    "implementation_time": "12-24 months",
                    "environmental_benefits": "Increased corridor wind speed,Local microclimate cooling,Restored species movement",
                    "sustainability_benefits": "SDG 15: Life on Land. Reconnects isolated urban green reserves.",
                    "confidence_score": 95.0,
                    "severity": "Critical"
                },
                {
                    "strategy_name": "Cool Roof Systems",
                    "category": "Cool Materials",
                    "reason": "Reduces building envelope absorption of extreme thermal radiation.",
                    "trigger_condition": f"LST = {lst:.1f}°C (>40°C), NDBI = {ndbi:.2f} (>0.55)",
                    "technical_explanation": "High SRI coatings reflect over 75% of solar radiation back to the sky, preventing concrete roofs from storing thermal energy.",
                    "recommended_implementation": "Apply elastomeric white reflective paint (SRI > 104) on all building roof decks.",
                    "priority_level": "Immediate",
                    "temp_reduction": 2.4,
                    "cost_level": "Medium",
                    "implementation_time": "3-6 months",
                    "environmental_benefits": "Lower internal room temperature,Reduced HVAC power grid demand,Lower heat emissions",
                    "sustainability_benefits": "SDG 7: Affordable Energy. Lowers cooling electricity bills during peak summer weeks.",
                    "confidence_score": 96.0,
                    "severity": "Critical"
                },
                {
                    "strategy_name": "Reflective Pavements",
                    "category": "Cool Materials",
                    "reason": "Reflects solar radiation from high-exposure streets and pathways.",
                    "trigger_condition": f"NDBI = {ndbi:.2f} (>0.55), LST = {lst:.1f}°C (>40°C)",
                    "technical_explanation": "Reflective binders prevent roads from absorbing sensible heat and radiating it back at night.",
                    "recommended_implementation": "Re-pave pedestrian paths and streets with high-albedo concrete sealants (albedo > 0.45).",
                    "priority_level": "Short Term",
                    "temp_reduction": 1.8,
                    "cost_level": "High",
                    "implementation_time": "12-24 months",
                    "environmental_benefits": "Lower road temperature,Improved pedestrian walking comfort",
                    "sustainability_benefits": "SDG 9: Industry & Infrastructure. Extends asphalt lifespan by reducing thermal cracking.",
                    "confidence_score": 91.0,
                    "severity": "Critical"
                },
                {
                    "strategy_name": "Vertical Living Walls",
                    "category": "Green Infrastructure",
                    "reason": "Uses vertical surfaces to shield building facades from absorbing heat.",
                    "trigger_condition": f"NDBI = {ndbi:.2f} (>0.55), NDVI = {ndvi:.2f} (<0.20)",
                    "technical_explanation": "Wall plant screens intercept direct sunlight, shading structural concrete blocks and lowering temperatures via transpiration.",
                    "recommended_implementation": "Install modular felt-pocket vertical irrigation walls seeded with native ferns.",
                    "priority_level": "Short Term",
                    "temp_reduction": 1.4,
                    "cost_level": "Medium",
                    "implementation_time": "3-6 months",
                    "environmental_benefits": "Shaded vertical facade surfaces,Facade noise dampening,Air filtering",
                    "sustainability_benefits": "SDG 3: Good Health. Filters PM10/PM2.5 particles to improve local air quality.",
                    "confidence_score": 88.0,
                    "severity": "Critical"
                },
                {
                    "strategy_name": "Rainwater Harvesting & Bioswales",
                    "category": "Green Infrastructure",
                    "reason": "Recharges soil water content to support latent heat cooling.",
                    "trigger_condition": f"NDVI = {ndvi:.2f} (<0.20), LST = {lst:.1f}°C (>40°C)",
                    "technical_explanation": "Directing stormwater runoff into retention bioswales feeds tree root zones, supporting transpiration.",
                    "recommended_implementation": "Construct graded rock-packed bioswales with grass borders around stormwater drains.",
                    "priority_level": "Long Term",
                    "temp_reduction": 1.0,
                    "cost_level": "Low",
                    "implementation_time": "6-12 months",
                    "environmental_benefits": "Water table recharge,Reduced stormwater runoff,Ambient air cooling",
                    "sustainability_benefits": "SDG 6: Clean Water. Protects local aquifer levels.",
                    "confidence_score": 89.0,
                    "severity": "Critical"
                }
            ])

        # ----------------------------------------------------
        # CASE 4: Industrial Areas (e.g. Peenya)
        is_industrial = land_cover == "industrial" or "peenya" in place_name.lower() or (ndbi > 0.60 and land_cover == "industrial")
        if is_industrial and not is_critical_hotspot:
            recommendations.extend([
                {
                    "strategy_name": "Industrial Green Belts",
                    "category": "Green Infrastructure",
                    "reason": "Establishes a thick perimeter tree buffer to block heat plume propagation.",
                    "trigger_condition": f"Land Cover = Industrial, NDBI = {ndbi:.2f} (>0.60)",
                    "technical_explanation": "A dense perimeter forest belt captures particulate dust, breaks wind speeds, and cools warm plumes through transpiration.",
                    "recommended_implementation": "Plant a 3-row Miyawaki forest belt using fast-growing native trees along industrial park borders.",
                    "priority_level": "Immediate" if lst > 38.0 else "Short Term",
                    "temp_reduction": 2.5,
                    "cost_level": "Medium",
                    "implementation_time": "12-18 months",
                    "environmental_benefits": "Plume cooling,Industrial dust capture,Buffer shielding",
                    "sustainability_benefits": "SDG 11: Sustainable Cities. Shields adjacent residential neighborhoods from industrial plumes.",
                    "confidence_score": 94.0,
                    "severity": "High"
                },
                {
                    "strategy_name": "Waste Heat Recovery",
                    "category": "Policy / Urban Planning",
                    "reason": "Prevents industrial processes from releasing hot waste gas into the air.",
                    "trigger_condition": f"Land Cover = Industrial, LST = {lst:.1f}°C",
                    "technical_explanation": "Thermal exchangers capture heat from process vents and recycle it into industrial boiler pre-heating loops.",
                    "recommended_implementation": "Install gas-to-liquid thermal exchangers on manufacturing exhaust stacks.",
                    "priority_level": "Short Term",
                    "temp_reduction": 1.8,
                    "cost_level": "High",
                    "implementation_time": "12-24 months",
                    "environmental_benefits": "Reduced thermal plume output,Lower factory fuel usage",
                    "sustainability_benefits": "SDG 9: Industry & Infrastructure. Enhances factory resource efficiency.",
                    "confidence_score": 90.0,
                    "severity": "High"
                },
                {
                    "strategy_name": "Reflective Factory Roofs",
                    "category": "Cool Materials",
                    "reason": "Cools metal factory roof sheets to limit overhead thermal plume release.",
                    "trigger_condition": f"Land Cover = Industrial, LST = {lst:.1f}°C",
                    "technical_explanation": "SRI-compliant coatings block solar heat absorption in metal roofs, keeping factory interiors cooler.",
                    "recommended_implementation": "Paint metal roofs with dual coats of white ceramic paint (SRI > 105).",
                    "priority_level": "Immediate",
                    "temp_reduction": 3.0,
                    "cost_level": "Medium",
                    "implementation_time": "3-6 months",
                    "environmental_benefits": "Cooler factory interiors,Lower air convective plume release",
                    "sustainability_benefits": "SDG 13: Climate Action. Offsets heavy factory HVAC loads.",
                    "confidence_score": 96.0,
                    "severity": "High"
                },
                {
                    "strategy_name": "Emission Reduction Systems",
                    "category": "Policy / Urban Planning",
                    "reason": "Restricts hot stack exhaust releases from boilers and ovens.",
                    "trigger_condition": f"Land Cover = Industrial, LST = {lst:.1f}°C",
                    "technical_explanation": "Vapor condensing scrubbers cool exhaust gases before they leave stacks, reducing localized ambient temperatures.",
                    "recommended_implementation": "Mandate exhaust condensing units for all factories with stacks venting over 80°C.",
                    "priority_level": "Short Term",
                    "temp_reduction": 1.2,
                    "cost_level": "High",
                    "implementation_time": "12-18 months",
                    "environmental_benefits": "Cooler stack exhaust,Reduced particulate emissions",
                    "sustainability_benefits": "SDG 3: Good Health. Improves regional air quality.",
                    "confidence_score": 89.0,
                    "severity": "High"
                },
                {
                    "strategy_name": "Cool Pavements",
                    "category": "Cool Materials",
                    "reason": "Reflects solar radiation from industrial parking yards and loading docks.",
                    "trigger_condition": f"NDBI = {ndbi:.2f} (>0.60)",
                    "technical_explanation": "Permeable high-albedo paving blocks release less sensible heat at night and reduce thermal radiation.",
                    "recommended_implementation": "Re-lay asphalt loading yards with light-colored permeable concrete blocks.",
                    "priority_level": "Short Term",
                    "temp_reduction": 1.5,
                    "cost_level": "High",
                    "implementation_time": "12-24 months",
                    "environmental_benefits": "Lower pavement surface temp,Reduced convective warming,Aquifer recharge",
                    "sustainability_benefits": "SDG 9: Industry & Infrastructure. Increases pavement durability under truck loads.",
                    "confidence_score": 91.0,
                    "severity": "High"
                },
                {
                    "strategy_name": "Buffer Plantations",
                    "category": "Green Infrastructure",
                    "reason": "Surrounds industrial boundaries with thick foliage to buffer surrounding zones.",
                    "trigger_condition": f"NDVI = {ndvi:.2f} (<0.20)",
                    "technical_explanation": "Dense tree canopies filter industrial particulate dust and trap warm convective air currents.",
                    "recommended_implementation": "Plant a 20-meter forest buffer zone along the industrial zone perimeter.",
                    "priority_level": "Long Term",
                    "temp_reduction": 2.0,
                    "cost_level": "Medium",
                    "implementation_time": "12-24 months",
                    "environmental_benefits": "Buffer shielding,Dust reduction,Plume cooling",
                    "sustainability_benefits": "SDG 15: Life on Land",
                    "confidence_score": 93.0,
                    "severity": "High"
                }
            ])

        # ----------------------------------------------------
        # CASE 5: Commercial Areas (e.g. Whitefield)
        is_commercial = land_cover == "commercial" or "whitefield" in place_name.lower() or land_cover == "retail"
        if is_commercial and not is_critical_hotspot:
            recommendations.extend([
                {
                    "strategy_name": "Cool Roof Systems",
                    "category": "Cool Materials",
                    "reason": "Cools large concrete commercial roof decks.",
                    "trigger_condition": f"Land Cover = Commercial, LST = {lst:.1f}°C",
                    "technical_explanation": "High SRI coatings reflect solar rays, preventing concrete structures from absorbing and storing heat.",
                    "recommended_implementation": "Apply dual coat high-reflectance paints with Solar Reflectance Index (SRI) > 104.",
                    "priority_level": "Immediate" if lst > 38.0 else "Short Term",
                    "temp_reduction": 2.2,
                    "cost_level": "Medium",
                    "implementation_time": "3-6 months",
                    "environmental_benefits": "Lower indoor temp,Reduced HVAC energy use,Reduced convective heat",
                    "sustainability_benefits": "SDG 7: Affordable Energy. Decreases HVAC power grid demands.",
                    "confidence_score": 93.0,
                    "severity": "High"
                },
                {
                    "strategy_name": "Reflective Glass Installation",
                    "category": "Cool Materials",
                    "reason": "Reduces solar heat gain through large glass building facades.",
                    "trigger_condition": f"Land Cover = Commercial, NDBI = {ndbi:.2f}",
                    "technical_explanation": "Reflective films block infrared solar wavelengths while letting visible light in, preventing glass facades from heating the street.",
                    "recommended_implementation": "Apply low-emissivity (Low-E) solar control window films to south-facing glass facades.",
                    "priority_level": "Short Term",
                    "temp_reduction": 1.0,
                    "cost_level": "Medium",
                    "implementation_time": "3-6 months",
                    "environmental_benefits": "Lower street convective heat,Reduced internal AC workload",
                    "sustainability_benefits": "SDG 13: Climate Action",
                    "confidence_score": 91.0,
                    "severity": "Moderate"
                },
                {
                    "strategy_name": "Green Walls",
                    "category": "Green Infrastructure",
                    "reason": "Shades vertical concrete walls of commercial complexes.",
                    "trigger_condition": f"Land Cover = Commercial, NDBI = {ndbi:.2f} (>0.45)",
                    "technical_explanation": "Facade foliage intercepts solar rays, preventing concrete walls from absorbing sensible heat.",
                    "recommended_implementation": "Install modular vertical wall panels planted with native ivy and ferns.",
                    "priority_level": "Short Term",
                    "temp_reduction": 1.4,
                    "cost_level": "Medium",
                    "implementation_time": "3-6 months",
                    "environmental_benefits": "Shaded vertical facade surfaces,Air filtering,Facade noise dampening",
                    "sustainability_benefits": "SDG 11: Sustainable Cities. Enhances urban visual aesthetics.",
                    "confidence_score": 88.0,
                    "severity": "High"
                },
                {
                    "strategy_name": "Rooftop Gardens",
                    "category": "Green Infrastructure",
                    "reason": "Replaces bare concrete commercial roofs with vegetative insulation.",
                    "trigger_condition": f"Land Cover = Commercial, NDVI = {ndvi:.2f} (<0.20)",
                    "technical_explanation": "Rooftop plant soil layers insulate the building and cool the ambient air via transpiration.",
                    "recommended_implementation": "Plant low-maintenance sedum grass layers over root-barrier membranes on reinforced flat rooftops.",
                    "priority_level": "Long Term",
                    "temp_reduction": 1.8,
                    "cost_level": "High",
                    "implementation_time": "12-18 months",
                    "environmental_benefits": "Rooftop thermal insulation,Lower localized air temp,Enhanced local biodiversity",
                    "sustainability_benefits": "SDG 11: Sustainable Cities. Adds local rooftop community gardens.",
                    "confidence_score": 90.0,
                    "severity": "High"
                },
                {
                    "strategy_name": "Shaded Parking Areas",
                    "category": "Green Infrastructure",
                    "reason": "Cools open-air commercial parking structures.",
                    "trigger_condition": f"Land Cover = Commercial, LST = {lst:.1f}°C",
                    "technical_explanation": "Greened parking structures block sunlight from striking dark asphalt parking areas.",
                    "recommended_implementation": "Install overhead steel frames covered with native creeping vines and solar panels.",
                    "priority_level": "Short Term",
                    "temp_reduction": 1.5,
                    "cost_level": "Medium",
                    "implementation_time": "3-6 months",
                    "environmental_benefits": "Lower parking lot temp,Reduced vehicle cabin heating",
                    "sustainability_benefits": "SDG 7: Affordable Energy. Generates clean solar electricity.",
                    "confidence_score": 92.0,
                    "severity": "Moderate"
                },
                {
                    "strategy_name": "Smart Building Materials",
                    "category": "Cool Materials",
                    "reason": "Uses phase-change construction materials to reduce sensible heat release.",
                    "trigger_condition": f"Land Cover = Commercial, NDBI = {ndbi:.2f}",
                    "technical_explanation": "Phase change materials absorb heat during the day and release it at night, balancing localized temperature shifts.",
                    "recommended_implementation": "Incorporate phase-change thermal panels into wall insulation layers during building retrofits.",
                    "priority_level": "Long Term",
                    "temp_reduction": 1.1,
                    "cost_level": "High",
                    "implementation_time": "12-24 months",
                    "environmental_benefits": "Smoothed diurnal thermal shifts,Lower peak summer interior cooling load",
                    "sustainability_benefits": "SDG 9: Industry & Innovation. Promotes smart construction materials.",
                    "confidence_score": 87.0,
                    "severity": "Moderate"
                }
            ])

        # ----------------------------------------------------
        # CASE 6: Residential Areas
        is_residential = land_cover == "residential" or "electronic" in place_name.lower() or land_cover == "neighborhood"
        if is_residential and not is_critical_hotspot:
            recommendations.extend([
                {
                    "strategy_name": "Community Parks Development",
                    "category": "Green Infrastructure",
                    "reason": "Develops community green spaces within residential neighborhoods.",
                    "trigger_condition": f"Land Cover = Residential, NDVI = {ndvi:.2f} (<0.30)",
                    "technical_explanation": "Grass and trees in community parks cool adjacent residential streets through transpiration.",
                    "recommended_implementation": "Acquire vacant residential plots to develop local parks with native trees.",
                    "priority_level": "Long Term",
                    "temp_reduction": 1.6,
                    "cost_level": "Medium",
                    "implementation_time": "6-12 months",
                    "environmental_benefits": "Neighborhood LST cooling,Soil water infiltration,Local recreational zones",
                    "sustainability_benefits": "SDG 11: Sustainable Cities. Enhances health and green space access.",
                    "confidence_score": 93.0,
                    "severity": "Moderate"
                },
                {
                    "strategy_name": "Roadside Tree Plantation",
                    "category": "Green Infrastructure",
                    "reason": "Shades residential streets and walkways.",
                    "trigger_condition": f"Land Cover = Residential, LST = {lst:.1f}°C",
                    "technical_explanation": "Street trees shade road pavements, preventing sensible heat absorption and release.",
                    "recommended_implementation": "Plant native street trees (e.g. Neem, Honge) at 6-meter intervals along residential walks.",
                    "priority_level": "Short Term",
                    "temp_reduction": 2.0,
                    "cost_level": "Low",
                    "implementation_time": "6-12 months",
                    "environmental_benefits": "Shaded street corridors,Improved air quality,Carbon sequestration",
                    "sustainability_benefits": "SDG 15: Life on Land. Re-establishes bird nesting pathways.",
                    "confidence_score": 95.0,
                    "severity": "Moderate"
                },
                {
                    "strategy_name": "Rain Gardens Installation",
                    "category": "Green Infrastructure",
                    "reason": "Uses residential runoff to irrigate roadside plants.",
                    "trigger_condition": f"Land Cover = Residential, NDVI = {ndvi:.2f}",
                    "technical_explanation": "Depressed rain gardens capture storm runoff, keeping soils damp to support plant transpiration.",
                    "recommended_implementation": "Construct 3x5 meter vegetated depressions along street drains.",
                    "priority_level": "Short Term",
                    "temp_reduction": 0.8,
                    "cost_level": "Low",
                    "implementation_time": "1-3 months",
                    "environmental_benefits": "Soil moisture conservation,Reduced street flooding,Corridor cooling",
                    "sustainability_benefits": "SDG 6: Clean Water. Minimizes urban flood surges.",
                    "confidence_score": 89.0,
                    "severity": "Moderate"
                },
                {
                    "strategy_name": "Household Rainwater Harvesting",
                    "category": "Policy / Urban Planning",
                    "reason": "Increases local water supply to maintain residential gardens.",
                    "trigger_condition": f"Land Cover = Residential, Humidity = {humidity}%",
                    "technical_explanation": "Storing rooftop runoff provides water for household plants, supporting evaporation cooling.",
                    "recommended_implementation": "Install sand-filter water harvesting tanks linked to residential roof pipes.",
                    "priority_level": "Long Term",
                    "temp_reduction": 0.4,
                    "cost_level": "Low",
                    "implementation_time": "3-6 months",
                    "environmental_benefits": "Aquifer recharging,Reduced municipal water demand,Damp microclimates",
                    "sustainability_benefits": "SDG 6: Clean Water & Sanitation",
                    "confidence_score": 92.0,
                    "severity": "Low"
                },
                {
                    "strategy_name": "Residential Green Roofs",
                    "category": "Green Infrastructure",
                    "reason": "Provides thermal insulation for residential concrete roofs.",
                    "trigger_condition": f"Land Cover = Residential, NDBI = {ndbi:.2f} (>0.40)",
                    "technical_explanation": "Rooftop plant soil layers insulate the building and cool the ambient air via transpiration.",
                    "recommended_implementation": "Install lightweight sedum grass modular trays on reinforced roofs.",
                    "priority_level": "Long Term",
                    "temp_reduction": 1.4,
                    "cost_level": "High",
                    "implementation_time": "12-18 months",
                    "environmental_benefits": "Reduced home heating,Lower AC usage,Enhanced local bird habitats",
                    "sustainability_benefits": "SDG 11: Sustainable Cities",
                    "confidence_score": 88.0,
                    "severity": "Moderate"
                }
            ])

        # ----------------------------------------------------
        # CASE 2: Moderate Hotspots (LST 35–40°C AND NDVI 0.20–0.40)
        is_case2 = (35.0 <= lst <= 40.0) and (0.20 <= ndvi <= 0.40)
        if is_case2 and not recommendations:
            recommendations.extend([
                {
                    "strategy_name": "Increase Roadside Vegetation",
                    "category": "Green Infrastructure",
                    "reason": "Increases vegetation along roadways to cool walking paths.",
                    "trigger_condition": f"LST = {lst:.1f}°C (35–40°C), NDVI = {ndvi:.2f} (0.20–0.40)",
                    "technical_explanation": "Dense shrubs and grasses along roads shade walking paths, reducing soil sensible heat.",
                    "recommended_implementation": "Plant multi-layered native shrubs along service road medians.",
                    "priority_level": "Short Term",
                    "temp_reduction": 1.4,
                    "cost_level": "Low",
                    "implementation_time": "6-12 months",
                    "environmental_benefits": "Cooler roadsides,Improved pedestrian comfort,Particulate capture",
                    "sustainability_benefits": "SDG 11: Sustainable Cities",
                    "confidence_score": 92.0,
                    "severity": "Moderate"
                },
                {
                    "strategy_name": "Green Parking Areas",
                    "category": "Green Infrastructure",
                    "reason": "Cools open-air commercial parking structures.",
                    "trigger_condition": f"LST = {lst:.1f}°C, NDBI = {ndbi:.2f}",
                    "technical_explanation": "Greened parking structures block sunlight from striking dark asphalt parking areas.",
                    "recommended_implementation": "Install overhead frames with native creeping vines.",
                    "priority_level": "Short Term",
                    "temp_reduction": 1.2,
                    "cost_level": "Medium",
                    "implementation_time": "3-6 months",
                    "environmental_benefits": "Lower parking lot temp,Reduced vehicle cabin heating",
                    "sustainability_benefits": "SDG 7: Affordable Energy",
                    "confidence_score": 90.0,
                    "severity": "Moderate"
                },
                {
                    "strategy_name": "Pocket Parks Development",
                    "category": "Green Infrastructure",
                    "reason": "Develops small green spaces within residential neighborhoods.",
                    "trigger_condition": f"NDVI = {ndvi:.2f} (0.20–0.40), LST = {lst:.1f}°C",
                    "technical_explanation": "Pocket parks provide pockets of cool air that reduce adjacent residential temperatures.",
                    "recommended_implementation": "Acquire vacant plots to develop small parks with native trees.",
                    "priority_level": "Long Term",
                    "temp_reduction": 1.5,
                    "cost_level": "Medium",
                    "implementation_time": "6-12 months",
                    "environmental_benefits": "Localized cooling,Soil moisture conservation",
                    "sustainability_benefits": "SDG 11: Sustainable Cities",
                    "confidence_score": 91.0,
                    "severity": "Moderate"
                },
                {
                    "strategy_name": "Rooftop Gardens",
                    "category": "Green Infrastructure",
                    "reason": "Replaces bare concrete commercial roofs with vegetative insulation.",
                    "trigger_condition": f"NDVI = {ndvi:.2f} (0.20–0.40), LST = {lst:.1f}°C",
                    "technical_explanation": "Rooftop plant soil layers insulate the building and cool the ambient air via transpiration.",
                    "recommended_implementation": "Plant low-maintenance sedum grass layers over root-barrier membranes.",
                    "priority_level": "Long Term",
                    "temp_reduction": 1.6,
                    "cost_level": "High",
                    "implementation_time": "12-18 months",
                    "environmental_benefits": "Rooftop thermal insulation,Lower localized air temp",
                    "sustainability_benefits": "SDG 11: Sustainable Cities",
                    "confidence_score": 89.0,
                    "severity": "Moderate"
                },
                {
                    "strategy_name": "Smart Irrigation Systems",
                    "category": "Urban Planning",
                    "reason": "Maintains canopy health during summer thermal cycles.",
                    "trigger_condition": f"LST = {lst:.1f}°C, Humidity = {humidity}%",
                    "technical_explanation": "Automated drip sensors maintain leaf moisture during heatwaves, ensuring evapotranspiration does not dry out.",
                    "recommended_implementation": "Deploy soil moisture telemetry linkages to municipal park sprinkler grids.",
                    "priority_level": "Long Term",
                    "temp_reduction": 0.8,
                    "cost_level": "Low",
                    "implementation_time": "3-6 months",
                    "environmental_benefits": "Protected canopy,Water conservation",
                    "sustainability_benefits": "SDG 6: Water Conservation",
                    "confidence_score": 88.0,
                    "severity": "Moderate"
                }
            ])

        # ----------------------------------------------------
        # Fallback Strategy Builder (Ensures we never return empty states)
        if not recommendations:
            recommendations.extend([
                {
                    "strategy_name": "Urban Tree Plantation",
                    "category": "Green Infrastructure",
                    "reason": f"Expands canopy shade to block direct solar radiation (NDVI: {ndvi:.2f}).",
                    "trigger_condition": f"NDVI = {ndvi:.2f} (<0.40), LST = {lst:.1f}°C",
                    "technical_explanation": "Tree leaves block solar radiation from heating concrete, and evaporate water to cool the air.",
                    "recommended_implementation": "Plant native street trees at 6-meter spacing along pedestrian paths.",
                    "priority_level": "Short Term",
                    "temp_reduction": 1.8,
                    "cost_level": "Medium",
                    "implementation_time": "6-12 months",
                    "environmental_benefits": "Lower surface temperature,Better air quality,Carbon sequestration",
                    "sustainability_benefits": "SDG 11: Sustainable Cities",
                    "confidence_score": 90.0,
                    "severity": "Moderate"
                },
                {
                    "strategy_name": "Cool Roof Systems",
                    "category": "Cool Materials",
                    "reason": f"Reflects solar radiation from building concrete roofs (LST: {lst:.1f}°C).",
                    "trigger_condition": f"LST = {lst:.1f}°C (>30°C)",
                    "technical_explanation": "High SRI coatings reflect over 75% of solar radiation back to the sky.",
                    "recommended_implementation": "Apply white reflective coatings (SRI > 104) on all building roof decks.",
                    "priority_level": "Short Term",
                    "temp_reduction": 1.5,
                    "cost_level": "Medium",
                    "implementation_time": "3-6 months",
                    "environmental_benefits": "Lower indoor temp,Reduced building energy consumption",
                    "sustainability_benefits": "SDG 7: Affordable Energy",
                    "confidence_score": 91.0,
                    "severity": "Moderate"
                },
                {
                    "strategy_name": "Permeable Cool Pavements",
                    "category": "Cool Materials",
                    "reason": f"Reduces pavement sensible heat absorption (NDBI: {ndbi:.2f}).",
                    "trigger_condition": f"NDBI = {ndbi:.2f} (>0.20)",
                    "technical_explanation": "Permeable materials lock moisture in soils, supporting cooling evaporation while reflecting solar energy.",
                    "recommended_implementation": "Re-lay standard concrete tiles with porous grid paving stones.",
                    "priority_level": "Long Term",
                    "temp_reduction": 1.2,
                    "cost_level": "High",
                    "implementation_time": "12-24 months",
                    "environmental_benefits": "Lower surface temp,Aquifer recharge",
                    "sustainability_benefits": "SDG 11: Sustainable Cities",
                    "confidence_score": 90.0,
                    "severity": "Moderate"
                }
            ])

        # Sort recommendations: Priority urgency first (Immediate=3, Short Term=2, Long Term=1)
        # then temp_reduction, then confidence_score
        priority_map = {"Immediate": 3, "Short Term": 2, "Long Term": 1}
        recommendations.sort(key=lambda x: (
            priority_map.get(x["priority_level"], 0), 
            x["temp_reduction"], 
            x["confidence_score"]
        ), reverse=True)

        return recommendations[:10]

    @staticmethod
    def generate_mitigation_summary(stats, hotspots):
        """
        Generates a comprehensive diagnostic report summary explaining the UHI causes,
        primary variables contributing to heat, and key cooling actions.
        """
        filename = stats.get("filename", "Active Dataset")
        is_bengaluru = False
        if hotspots:
            avg_lat = sum(h["latitude"] for h in hotspots) / len(hotspots)
            avg_lon = sum(h["longitude"] for h in hotspots) / len(hotspots)
            is_bengaluru = 12.0 < avg_lat < 14.0 and 76.5 < avg_lon < 78.5
            
        region = "Bengaluru, Karnataka" if is_bengaluru else "the analyzed region"
        
        critical_lst = sum(1 for h in hotspots if h["lst"] >= 42.0)
        low_ndvi = sum(1 for h in hotspots if h["ndvi"] < 0.20)
        high_ndbi = sum(1 for h in hotspots if h["ndbi"] > 0.45)
        
        max_variable = "LST"
        if low_ndvi > high_ndbi:
            max_variable = "NDVI (Lack of Vegetation)"
            cause_description = (
                "a critical deficit in green canopy cover. Evapotranspiration cooling is absent "
                "in these sectors, leading to massive heating of exposed dry soils."
            )
        elif high_ndbi >= low_ndvi:
            max_variable = "NDBI (High Built-up Density)"
            cause_description = (
                "the high density of impervious concrete and asphalt structures. These materials "
                "act as active thermal sinks, storing solar radiation and creating severe convective plumes."
            )
        else:
            cause_description = "extreme solar radiation loading on dry, bare soils."
            
        action_text = ""
        if is_bengaluru:
            action_text = (
                "Specific local interventions have been generated: target cool roofing for **Peenya Industrial sheds** "
                "to block metal heat storage, plant green corridors around **Electronic City IT parks**, and enforce linear "
                "shade canopies along the **Outer Ring Road** highway. Additionally, hydrological wetlands around **Bellandur "
                "and Varthur lakes** must be protected to restore Bangalore's natural cooling buffer."
            )
        else:
            action_text = (
                "Prioritize cool roof reflective coatings on flat roofs to achieve low-cost, high-speed temperature reduction. "
                "De-pave unutilized parking lanes, and replace standard asphalt with permeable cool concrete. Establish pocket parks "
                "to re-introduce active evapotranspiration cooling."
            )

        summary_md = f"""### UHI Mitigation Assessment Report ({region})

**Diagnostic Analysis for dataset `{filename}`:**
The heat island hotspots in this dataset primarily exist due to **{cause_description}**

**Primary Climatic Variables Contributing to Heat:**
1. **{max_variable}**: Detected as the dominant driver of heat accumulation. Wards with NDBI > 0.45 show surface temperatures up to 8.5°C higher than green zones.
2. **Surface Thermal Albedo (LST)**: {critical_lst} critical locations exceeded 42°C, requiring immediate emergency heat action policies.
3. **Vegetation Canopy Index**: {low_ndvi} sectors show NDVI < 0.20, pointing to severe canopy gaps.

**Key Cooling Strategies & Impact Summary:**
- **Reflective Cool Roofs**: Yields the highest expected immediate reduction of **-2.8°C to -4.0°C** LST.
- **Urban Forestry**: Provides long-term environmental protection and offsets up to 35 tons of CO₂/yr/1000m² of tree cover.
- **Hydrological Restoration**: Restores natural water cooling loops.

*Urban Action Blueprint:* {action_text}
"""
        return summary_md
