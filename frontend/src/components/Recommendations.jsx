import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Search, 
  Filter, 
  TrendingDown, 
  DollarSign, 
  Leaf, 
  Layers,
  ArrowRight,
  Percent,
  CheckCircle,
  Clock,
  ChevronDown,
  ChevronUp,
  Globe,
  Activity,
  FileText,
  Droplets,
  Thermometer,
  ShieldAlert,
  HelpCircle,
  Zap,
  ArrowUpRight
} from 'lucide-react';

const Recommendations = ({ 
  datasetId, 
  summary, 
  selectedLocation, 
  locationRecs, 
  recsLoading, 
  setActiveTab 
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPriority, setSelectedPriority] = useState('all');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [expandedCardId, setExpandedCardId] = useState(null);

  const getPriorityBadgeClass = (priority) => {
    switch (priority) {
      case 'Immediate': return 'bg-red-500/10 text-red-400 border-red-500/20';
      case 'Short Term': return 'bg-orange-500/10 text-orange-400 border-orange-500/20';
      default: return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20';
    }
  };

  const getSeverityBadgeClass = (severity) => {
    switch (severity) {
      case 'Critical': return 'text-red-400 bg-red-950/30 border-red-900/50';
      case 'High': return 'text-orange-400 bg-orange-950/30 border-orange-900/50';
      case 'Moderate': return 'text-yellow-400 bg-yellow-950/30 border-yellow-900/50';
      default: return 'text-emerald-400 bg-emerald-950/30 border-emerald-900/50';
    }
  };

  const getCostBadgeClass = (cost) => {
    switch (cost) {
      case 'High': return 'text-rose-400 bg-rose-950/20 border-rose-900/30';
      case 'Medium': return 'text-amber-400 bg-amber-950/20 border-amber-900/30';
      default: return 'text-emerald-400 bg-emerald-950/20 border-emerald-900/30';
    }
  };

  const getProgressTracker = (priority) => {
    switch (priority) {
      case 'Immediate': return { label: 'Immediate Planning Phase', pct: 25 };
      case 'Short Term': return { label: 'Strategic Tendering', pct: 55 };
      default: return { label: 'Detailed Design Studies', pct: 15 };
    }
  };

  const calculateAirTemp = (lst) => lst - 3.5;
  
  const calculateHumidity = (ndvi) => {
    const computed = 40 + ndvi * 50;
    return Math.max(15, Math.min(95, Math.round(computed)));
  };

  const calculateHeatIndex = (tempC, humidity) => {
    const T = tempC * 9/5 + 32;
    const R = humidity;
    const hi = 0.5 * (T + 61.0 + ((T - 68.0) * 1.2) + (R * 0.094));
    const hiC = (hi - 32) * 5/9;
    return Math.max(tempC, Math.round(hiC * 10) / 10);
  };

  const getPrimaryCause = (loc) => {
    const ndvi = loc.ndvi;
    const ndbi = loc.ndbi;
    if (ndvi < 0.20 && ndbi > 0.45) {
      return "High land surface temperature caused by dense built-up infrastructure, high impervious surface ratio (NDBI), limited vegetation cover (low NDVI), and low evapotranspiration.";
    } else if (ndvi < 0.20) {
      return "Elevated thermal loading caused by severe canopy deficit, lack of vegetated cover (low NDVI), and limited latent heat buffer capacity.";
    } else if (ndbi > 0.45) {
      return "High sensible heat retention caused by concrete built-up blocks (high NDBI) absorbing thermal radiation throughout solar exposure cycles.";
    } else {
      return "Baseline heat concentration driven by convective air movement and surrounding urban morphology conditions.";
    }
  };

  // If no location context is active, show instructions to go to the Map
  if (!selectedLocation) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-8 max-h-screen">
        <div className="flex flex-col items-center text-center p-10 max-w-md gap-5 border border-dashed border-slate-800 rounded-3xl bg-slate-950/20 glass-panel">
          <Globe className="w-16 h-16 text-slate-600 border border-slate-800 p-4 rounded-3xl bg-slate-900/30 animate-pulse" />
          <div>
            <h3 className="font-heading font-extrabold text-slate-200 text-lg">No Active Analysis Context</h3>
            <p className="text-slate-500 text-xs mt-2 leading-relaxed font-semibold">
              Select a location on the GIS Heat Map to generate AI-powered mitigation strategies.
            </p>
          </div>
          <button 
            onClick={() => setActiveTab && setActiveTab('heatmap')}
            className="px-5 py-2.5 bg-gradient-to-r from-emerald-500 to-cyan-500 text-slate-950 font-bold rounded-xl text-xs hover:shadow-lg transition-all"
          >
            Open GIS Heat Map
          </button>
        </div>
      </div>
    );
  }

  // Derive location statistics
  const airTemp = calculateAirTemp(selectedLocation.lst);
  const humidity = calculateHumidity(selectedLocation.ndvi);
  const heatIndex = calculateHeatIndex(airTemp, humidity);
  const vegCoverage = Math.round(selectedLocation.vegetation_density || ((selectedLocation.ndvi + 1) * 50));
  const primaryCause = getPrimaryCause(selectedLocation);

  // Compute dynamic AI Climate impact parameters
  const isHealthy = selectedLocation.risk_level?.toLowerCase() === 'low' || (selectedLocation.ndvi > 0.70 && selectedLocation.lst < 30.0);
  
  // Calculate dynamic confidence score based on environmental variables count
  const variables = [
    selectedLocation.lst,
    selectedLocation.ndvi,
    selectedLocation.ndbi,
    selectedLocation.land_cover,
    selectedLocation.vegetation_density,
    selectedLocation.risk_level
  ];
  const availableCount = variables.filter(v => v !== undefined && v !== null && v !== "").length;
  let confidenceText = "98% – Complete dataset";
  let confidenceValue = 98;
  if (availableCount < 4) {
    confidenceText = "65% – Limited environmental information";
    confidenceValue = 65;
  } else if (availableCount < 5) {
    confidenceText = "78% – Partial dataset";
    confidenceValue = 78;
  } else if (availableCount < 6) {
    confidenceText = "90% – Minor missing values";
    confidenceValue = 90;
  }

  let expectedCooling = 0.0;
  let predictedTemp = selectedLocation.lst;
  let summaryText = "";
  
  const placeName = selectedLocation.name || "the selected location";
  const coverType = (selectedLocation.land_cover || "Residential").toLowerCase();
  
  if (isHealthy) {
    expectedCooling = 0.3; // safe baseline cooling
    predictedTemp = Math.round((selectedLocation.lst - expectedCooling) * 10) / 10;
    summaryText = `No major mitigation is recommended. Maintaining the existing canopy and protecting biodiversity at ${placeName} will preserve the current thermal balance.`;
  } else {
    // Sum only recommended strategies for this location (locationRecs)
    const topRecs = locationRecs.slice(0, 3);
    const sumCooling = topRecs.reduce((acc, curr) => acc + (curr.temp_reduction || 1.5), 0);
    expectedCooling = Math.round(Math.min(5.5, sumCooling) * 10) / 10;
    predictedTemp = Math.round((selectedLocation.lst - expectedCooling) * 10) / 10;
    
    if (placeName.toLowerCase().includes("lake") || placeName.toLowerCase().includes("wetland") || coverType === "water") {
      summaryText = `Lake restoration and riparian vegetation improvements at ${placeName} are expected to improve evaporative cooling and reduce surrounding temperatures by approximately ${expectedCooling.toFixed(1)}°C.`;
    } else if (placeName.toLowerCase().includes("peenya") || coverType === "industrial") {
      summaryText = `Deploying industrial green belts, waste heat recovery, and reflective factory roofs at ${placeName} is expected to lower overhead thermal plume release and reduce temperatures by approximately ${expectedCooling.toFixed(1)}°C.`;
    } else if (placeName.toLowerCase().includes("whitefield") || coverType === "commercial" || coverType === "retail") {
      summaryText = `Combining cool roofs, vertical living walls, and commercial green roofs at ${placeName} is modeled to reduce average surface temperatures by approximately ${expectedCooling.toFixed(1)}°C.`;
    } else if (placeName.toLowerCase().includes("electronic") || coverType === "residential") {
      summaryText = `Integrating community parks, roadside tree plantations, and household rainwater harvesting at ${placeName} is expected to mitigate localized heat by approximately ${expectedCooling.toFixed(1)}°C.`;
    } else {
      summaryText = `Combining cool roofs, reflective pavements and urban tree planting at ${placeName} is expected to reduce average surface temperature by approximately ${expectedCooling.toFixed(1)}°C over the implementation period.`;
    }
  }

  const filteredRecs = locationRecs.filter(r => {
    const matchesSearch = r.strategy_name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesPriority = selectedPriority === 'all' || r.priority_level === selectedPriority;
    const matchesCategory = selectedCategory === 'all' || r.category === selectedCategory;
    return matchesSearch && matchesPriority && matchesCategory;
  });

  const toggleExpandCard = (id, e) => {
    e.stopPropagation();
    setExpandedCardId(expandedCardId === id ? null : id);
  };

  return (
    <div className="flex-1 flex flex-col gap-6 overflow-y-auto p-8 max-h-screen">
      
      {/* Dynamic Header */}
      <div className="border-b border-slate-800 pb-4">
        <span className="text-[10px] text-slate-500 font-extrabold uppercase tracking-widest">
          Climate Mitigation Decision Support System
        </span>
        <h2 className="text-3xl font-heading font-extrabold tracking-tight text-white mt-1">
          {selectedLocation.name}
        </h2>
      </div>

      {/* Main Stats and AI Predicted Card Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        
        {/* Environmental parameters of location */}
        <div className="lg:col-span-2 grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl border border-slate-850 bg-slate-900/10 flex flex-col gap-1">
            <span className="text-[9px] text-slate-500 font-bold uppercase tracking-wider flex items-center gap-1.5">
              <Thermometer className="w-3.5 h-3.5 text-orange-400" />
              Surface Temp (LST)
            </span>
            <span className="text-xl font-extrabold text-slate-100 mt-1">
              {selectedLocation.lst.toFixed(1)}°C
            </span>
          </div>

          <div className="p-4 rounded-xl border border-slate-850 bg-slate-900/10 flex flex-col gap-1">
            <span className="text-[9px] text-slate-500 font-bold uppercase tracking-wider flex items-center gap-1.5">
              <Droplets className="w-3.5 h-3.5 text-cyan-400" />
              Humidity
            </span>
            <span className="text-xl font-extrabold text-slate-100 mt-1">
              {humidity}%
            </span>
          </div>

          <div className="p-4 rounded-xl border border-slate-850 bg-slate-900/10 flex flex-col gap-1">
            <span className="text-[9px] text-slate-500 font-bold uppercase tracking-wider flex items-center gap-1.5">
              <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
              Heat Index
            </span>
            <span className="text-xl font-extrabold text-slate-100 mt-1">
              {heatIndex.toFixed(1)}°C
            </span>
          </div>

          <div className="p-4 rounded-xl border border-slate-850 bg-slate-900/10 flex flex-col gap-1">
            <span className="text-[9px] text-slate-500 font-bold uppercase tracking-wider flex items-center gap-1.5">
              <Leaf className="w-3.5 h-3.5 text-emerald-400" />
              Veg Coverage
            </span>
            <span className="text-xl font-extrabold text-slate-100 mt-1">
              {vegCoverage}%
            </span>
          </div>

          <div className="p-4 rounded-xl border border-slate-850 bg-slate-900/10 flex flex-col gap-1">
            <span className="text-[9px] text-slate-500 font-bold uppercase tracking-wider flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-blue-400" />
              NDVI / NDBI
            </span>
            <span className="text-base font-extrabold text-slate-100 mt-1">
              {selectedLocation.ndvi.toFixed(2)} / {selectedLocation.ndbi.toFixed(2)}
            </span>
          </div>

          <div className="p-4 rounded-xl border border-slate-850 bg-slate-900/10 flex flex-col gap-1">
            <span className="text-[9px] text-slate-500 font-bold uppercase tracking-wider flex items-center gap-1.5">
              <Globe className="w-3.5 h-3.5 text-teal-400" />
              Land Cover
            </span>
            <span className="text-base font-extrabold text-slate-200 mt-1 truncate">
              {selectedLocation.land_cover || 'Commercial'}
            </span>
          </div>

          <div className="p-4 rounded-xl border border-slate-850 bg-slate-900/10 flex flex-col gap-1">
            <span className="text-[9px] text-slate-500 font-bold uppercase tracking-wider flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-amber-400" />
              Built-up Density
            </span>
            <span className="text-base font-extrabold text-slate-100 mt-1">
              {Math.round((selectedLocation.ndbi + 1) * 50)}%
            </span>
          </div>

          <div className="p-4 rounded-xl border border-slate-850 bg-slate-900/10 flex flex-col gap-1">
            <span className="text-[9px] text-slate-500 font-bold uppercase tracking-wider flex items-center gap-1.5">
              <ShieldAlert className="w-3.5 h-3.5 text-indigo-400" />
              Risk Level
            </span>
            <span className={`text-base font-extrabold inline-flex mt-1 items-center px-2 py-0.5 rounded-md border w-fit ${getSeverityBadgeClass(selectedLocation.risk_level || 'High')}`}>
              {selectedLocation.risk_level || 'High'}
            </span>
          </div>
        </div>

        {/* AI Predicted Temperature Reduction Card */}
        <div className="p-5 rounded-2xl border border-emerald-500/20 bg-gradient-to-br from-emerald-950/20 to-slate-950/50 flex flex-col justify-between shadow-lg relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/5 rounded-full blur-2xl" />
          <div className="flex justify-between items-start">
            <div className="flex flex-col gap-1">
              <span className="text-[10px] text-emerald-400 font-extrabold uppercase tracking-widest flex items-center gap-1.5 font-heading">
                <Zap className="w-3.5 h-3.5" />
                AI Predicted Climate Prediction
              </span>
              <span className="text-[9px] text-slate-500 font-semibold mt-0.5">{confidenceText}</span>
            </div>
            <span className="px-2 py-0.5 border border-emerald-500/30 text-emerald-400 bg-emerald-950/30 rounded-md text-[9px] font-extrabold uppercase">
              {confidenceValue}% Cert.
            </span>
          </div>

          {isHealthy ? (
            <div className="border-t border-b border-slate-800/60 py-4 my-4 flex flex-col gap-1">
              <div className="text-[10px] text-emerald-400 font-extrabold uppercase tracking-widest">
                Status: Healthy Climate Zone
              </div>
              <div className="grid grid-cols-2 gap-2 mt-2 text-xs font-semibold text-slate-400">
                <div>
                  <span>Expected Cooling</span>
                  <span className="text-emerald-400 block text-lg font-extrabold mt-0.5">0.2–0.5°C</span>
                </div>
                <div>
                  <span>Predicted Temp</span>
                  <span className="text-slate-100 block text-lg font-extrabold mt-0.5">{selectedLocation.lst.toFixed(1)}°C → {predictedTemp.toFixed(1)}°C</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-3 gap-2 border-t border-b border-slate-800/60 py-4 my-4 text-xs font-semibold text-slate-400">
              <div className="flex flex-col">
                <span>Current</span>
                <span className="text-slate-100 text-lg font-extrabold mt-0.5">{selectedLocation.lst.toFixed(1)}°C</span>
              </div>
              <div className="flex flex-col">
                <span>Expected Cooling</span>
                <span className="text-emerald-400 text-lg font-extrabold mt-0.5">-{expectedCooling.toFixed(1)}°C</span>
              </div>
              <div className="flex flex-col">
                <span>Predicted Temp</span>
                <span className="text-slate-100 text-lg font-extrabold mt-0.5">{predictedTemp.toFixed(1)}°C</span>
              </div>
            </div>
          )}

          <p className="text-[10px] text-slate-300 font-semibold leading-relaxed">
            {isHealthy ? (
              <span>The selected location already maintains a stable microclimate. Major mitigation projects are unnecessary. Focus on preserving existing vegetation and preventing future degradation.</span>
            ) : (
              <span>{summaryText}</span>
            )}
          </p>
        </div>

      </div>

      {/* Root Cause Analysis Panel */}
      <div className="p-5 rounded-2xl border border-slate-800 bg-slate-900/10 flex flex-col gap-2">
        <span className="text-[10px] text-slate-500 font-extrabold uppercase tracking-widest flex items-center gap-1.5">
          <Activity className="w-4 h-4 text-emerald-400" />
          Root Cause Analysis
        </span>
        <p className="text-slate-300 font-semibold text-xs leading-relaxed mt-1">
          {primaryCause}
        </p>
      </div>

      {/* Filters Toolbar */}
      <div className="p-4 rounded-2xl bg-slate-900/40 border border-slate-800 flex flex-col md:flex-row gap-4 items-center justify-between">
        <div className="relative w-full md:w-80">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4.5 h-4.5 text-slate-500" />
          <input
            type="text"
            placeholder="Search location strategies..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-950/60 border border-slate-800 rounded-xl py-2 pl-10 pr-4 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500/40"
          />
        </div>

        <div className="flex w-full md:w-auto gap-3 items-center">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-400" />
            <span className="text-xs font-semibold text-slate-400">Filter:</span>
          </div>

          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="bg-slate-950 border border-slate-850 rounded-xl px-3 py-2 text-xs font-semibold text-slate-300 focus:outline-none"
          >
            <option value="all">All Categories</option>
            <option value="Green Infrastructure">Green Infrastructure</option>
            <option value="Cool Materials">Cool Materials</option>
            <option value="Policy / Urban Planning">Policy / Urban Planning</option>
          </select>

          <select
            value={selectedPriority}
            onChange={(e) => setSelectedPriority(e.target.value)}
            className="bg-slate-950 border border-slate-850 rounded-xl px-3 py-2 text-xs font-semibold text-slate-300 focus:outline-none"
          >
            <option value="all">All Priorities</option>
            <option value="Immediate">Immediate</option>
            <option value="Short Term">Short Term</option>
            <option value="Long Term">Long Term</option>
          </select>
        </div>
      </div>

      {/* Grid of Dynamic Recommendations */}
      {recsLoading ? (
        <div className="flex-1 py-20 flex flex-col items-center justify-center gap-3">
          <span className="w-6 h-6 rounded-full border-2 border-emerald-400 border-t-transparent animate-spin" />
          <span className="text-xs text-slate-400">Running dynamic rule heuristics...</span>
        </div>
      ) : (
        <div className="flex-1 min-h-0 flex flex-col gap-4">
          <div className="flex justify-between items-center text-xs font-bold text-slate-400 px-1">
            <span>{filteredRecs.length} ADAPTATION PLANS GENERATED FOR THIS WARD</span>
            <span>RANKED BY EXPECTED COOLING EFFECTIVENESS</span>
          </div>
          
          <div className="flex-1 overflow-y-auto flex flex-col gap-4 pr-1">
            <AnimatePresence mode="popLayout">
              {filteredRecs.map((rec) => {
                const isExpanded = expandedCardId === rec.id;
                const progress = getProgressTracker(rec.priority_level);
                return (
                  <motion.div
                    key={rec.id || rec.strategy_name}
                    layout
                    initial={{ opacity: 0, y: 15 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    className="rounded-2xl glass-panel p-5 border border-slate-800/80 flex flex-col gap-4 overflow-hidden cursor-pointer"
                    onClick={(e) => toggleExpandCard(rec.id, e)}
                  >
                    {/* Top Row Header */}
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
                      <div>
                        <h4 className="font-heading font-extrabold text-slate-100 text-base flex items-center gap-2">
                          Strategy {filteredRecs.indexOf(rec) + 1}: {rec.strategy_name}
                        </h4>
                        <div className="flex flex-wrap items-center gap-2 mt-1.5 text-xs text-slate-400">
                          <span className="text-emerald-400 font-semibold">{selectedLocation.name}</span>
                          <span>&bull;</span>
                          <span>Category: <b className="text-slate-200">{rec.category}</b></span>
                        </div>
                      </div>

                      {/* Badges Panel */}
                      <div className="flex flex-wrap items-center gap-2">
                        <span className={`px-2.5 py-0.5 border text-[9px] font-extrabold uppercase tracking-wider rounded-full ${getPriorityBadgeClass(rec.priority_level)}`}>
                          {rec.priority_level}
                        </span>
                        
                        <span className={`px-2.5 py-0.5 border border-slate-800 text-[9px] font-extrabold uppercase tracking-wider rounded-full text-slate-400`}>
                          SRI Rating {rec.confidence_score > 92 ? 'Class A' : 'Class B'}
                        </span>
                      </div>
                    </div>

                    {/* Why this strategy is recommended */}
                    <div className="p-3 bg-slate-950/40 border border-slate-900 rounded-xl text-xs flex items-start gap-2.5">
                      <Activity className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                      <p className="text-slate-300 font-semibold leading-relaxed">
                        <span className="text-slate-500 uppercase tracking-wider font-extrabold text-[9px] mr-1.5">Direct Trigger:</span>
                        {rec.reason}
                      </p>
                    </div>

                    {/* Metric Numbers Grid */}
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-3 bg-slate-900/20 p-3.5 border border-slate-850 rounded-xl text-xs">
                      <div className="flex flex-col gap-0.5">
                        <span className="text-[9px] text-slate-500 uppercase tracking-wider font-bold flex items-center gap-1">
                          <TrendingDown className="w-3.5 h-3.5 text-emerald-400" />
                          Expected Cooling
                        </span>
                        <span className="font-extrabold text-slate-200 text-sm">
                          {(rec.temp_reduction - 0.5 < 0 ? 0.5 : rec.temp_reduction - 0.5).toFixed(1)}–{(rec.temp_reduction + 0.5).toFixed(1)}°C
                        </span>
                      </div>

                      <div className="flex flex-col gap-0.5">
                        <span className="text-[9px] text-slate-500 uppercase tracking-wider font-bold flex items-center gap-1">
                          <Clock className="w-3.5 h-3.5 text-cyan-400" />
                          Implementation
                        </span>
                        <span className="font-extrabold text-slate-200 text-sm">
                          {rec.implementation_time || '6-12 months'}
                        </span>
                      </div>

                      <div className="flex flex-col gap-0.5">
                        <span className="text-[9px] text-slate-500 uppercase tracking-wider font-bold flex items-center gap-1">
                          <DollarSign className="w-3.5 h-3.5 text-orange-400" />
                          Estimated Cost
                        </span>
                        <span className="font-extrabold text-slate-200 text-sm">
                          {rec.cost_level || 'Medium'}
                        </span>
                      </div>

                      <div className="flex flex-col gap-0.5">
                        <span className="text-[9px] text-slate-500 uppercase tracking-wider font-bold flex items-center gap-1">
                          <Percent className="w-3.5 h-3.5 text-purple-400" />
                          Confidence
                        </span>
                        <span className="font-extrabold text-slate-200 text-sm">
                          {rec.confidence_score.toFixed(0)}%
                        </span>
                      </div>

                      <div className="flex flex-col gap-0.5">
                        <span className="text-[9px] text-slate-500 uppercase tracking-wider font-bold flex items-center gap-1">
                          <Globe className="w-3.5 h-3.5 text-teal-400" />
                          SDG Targets
                        </span>
                        <span className="font-extrabold text-slate-300 text-[10px] truncate mt-0.5" title={rec.sdg_alignment}>
                          {rec.sdg_alignment ? rec.sdg_alignment.split('|')[0] : 'SDG 11'}
                        </span>
                      </div>
                    </div>

                    {/* Expandable Details Container */}
                    <AnimatePresence>
                      {isExpanded && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          exit={{ opacity: 0, height: 0 }}
                          transition={{ duration: 0.2 }}
                          className="border-t border-slate-800/80 pt-4 flex flex-col gap-4 text-xs overflow-hidden"
                        >
                          {/* AI Reasoning Section */}
                          <div className="p-4 rounded-xl border border-emerald-500/20 bg-emerald-950/5 flex flex-col gap-2">
                            <span className="text-[10px] text-emerald-400 font-extrabold uppercase tracking-widest flex items-center gap-1.5 font-heading">
                              <Zap className="w-3.5 h-3.5" />
                              AI Reasoning &amp; Inference
                            </span>
                            <div className="text-xs font-semibold text-slate-300 flex flex-col gap-1.5 mt-1">
                              <p>
                                <span className="text-slate-500 mr-2 uppercase text-[9px] tracking-wider font-bold">Why Selected:</span>
                                {rec.strategy_name} was dynamically chosen because:
                              </p>
                              <p className="pl-3 border-l-2 border-emerald-500/30 py-1">
                                <span className="text-slate-400 mr-2 font-bold uppercase text-[9px]">Measured Parameters:</span>
                                <code className="bg-slate-950/80 px-2 py-0.5 rounded text-emerald-400 font-mono text-[11px] font-bold">
                                  {rec.trigger_condition || `LST = ${selectedLocation.lst.toFixed(1)}°C, NDVI = ${selectedLocation.ndvi.toFixed(2)}, NDBI = ${selectedLocation.ndbi.toFixed(2)}`}
                                </code>
                              </p>
                              <p>
                                <span className="text-slate-400 mr-2 font-bold uppercase text-[9px]">Trigger Justification:</span>
                                {rec.reason}
                              </p>
                            </div>
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="flex flex-col gap-1.5 bg-slate-900/10 p-3 rounded-xl border border-slate-850">
                              <span className="text-[9px] text-emerald-400 font-extrabold uppercase tracking-widest">Technical Explanation</span>
                              <p className="text-slate-300 leading-relaxed font-semibold">
                                {rec.technical_explanation || 'No technical metadata provided.'}
                              </p>
                            </div>

                            <div className="flex flex-col gap-1.5 bg-slate-900/10 p-3 rounded-xl border border-slate-850">
                              <span className="text-[9px] text-cyan-400 font-extrabold uppercase tracking-widest">Recommended Implementation</span>
                              <p className="text-slate-300 leading-relaxed font-semibold">
                                {rec.recommended_implementation || 'No recommended implementation guidelines provided.'}
                              </p>
                            </div>
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="flex flex-col gap-1.5">
                              <span className="text-[9px] text-slate-500 font-extrabold uppercase tracking-widest">Environmental Benefits</span>
                              <ul className="list-disc list-inside text-slate-300 leading-relaxed font-semibold flex flex-col gap-1 pl-1">
                                {rec.environmental_benefits ? (
                                  rec.environmental_benefits.split(',').map((benefit, bIdx) => (
                                    <li key={bIdx}>{benefit.trim()}</li>
                                  ))
                                ) : (
                                  <li>Lower surface temperature</li>
                                )}
                              </ul>
                            </div>

                            <div className="flex flex-col gap-1.5">
                              <span className="text-[9px] text-slate-500 font-extrabold uppercase tracking-widest">Sustainability &amp; SDG Benefits</span>
                              <p className="text-slate-300 leading-relaxed font-semibold">
                                {rec.sustainability_benefits || 'Promotes carbon mitigation and microclimate cooling.'}
                              </p>
                            </div>
                          </div>

                          {/* Progress Tracker bar */}
                          <div className="flex flex-col gap-2 p-3 bg-slate-950/30 border border-slate-900 rounded-xl mt-1">
                            <div className="flex justify-between items-center text-[10px] font-bold">
                              <span className="text-slate-400 flex items-center gap-1.5">
                                <Clock className="w-3.5 h-3.5 text-emerald-400" />
                                {progress.label}
                              </span>
                              <span className="text-emerald-400">{progress.pct}%</span>
                            </div>
                            <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden border border-slate-850">
                              <div 
                                className="bg-gradient-to-r from-emerald-500 to-cyan-500 h-full rounded-full"
                                style={{ width: `${progress.pct}%` }}
                              />
                            </div>
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>

                    {/* Expand/Collapse Indicator */}
                    <div className="flex justify-center border-t border-slate-850 pt-2.5 text-slate-500 group-hover:text-slate-300">
                      {isExpanded ? (
                        <ChevronUp className="w-4 h-4" />
                      ) : (
                        <ChevronDown className="w-4 h-4" />
                      )}
                    </div>
                  </motion.div>
                );
              })}
            </AnimatePresence>

            {filteredRecs.length === 0 && (
              <div className="py-20 text-center text-slate-500 border border-dashed border-slate-800 rounded-2xl">
                No adaptive blueprints match the selected filter parameters.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Recommendations;
