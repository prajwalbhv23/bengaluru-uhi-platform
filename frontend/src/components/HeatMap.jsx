import React, { useState, useEffect } from 'react';
import { 
  MapContainer, 
  TileLayer, 
  GeoJSON, 
  CircleMarker, 
  Popup,
  useMapEvents
} from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { mapAPI, recommendAPI } from '../utils/api';
import { 
  Flame, 
  Leaf, 
  Building, 
  ArrowDownToLine, 
  DollarSign,
  Activity,
  Droplets,
  Wind,
  ShieldAlert,
  Percent,
  CheckCircle,
  HelpCircle,
  Compass,
  TrendingDown
} from 'lucide-react';

// Custom event listener subcomponent to handle clicks anywhere on the Leaflet map
const MapClickHandler = ({ onClick }) => {
  useMapEvents({
    click: (e) => {
      onClick(e.latlng);
    }
  });
  return null;
};

// Map listener to record bounds and zoom for responsive rendering
const MapStateListener = ({ onChange }) => {
  const map = useMapEvents({
    zoomend: () => onChange(map.getZoom(), map.getBounds()),
    moveend: () => onChange(map.getZoom(), map.getBounds()),
  });
  React.useEffect(() => {
    onChange(map.getZoom(), map.getBounds());
  }, []);
  return null;
};

const HeatMap = ({ 
  datasetId, 
  selectedPoint, 
  setSelectedPoint, 
  customRecs, 
  setCustomRecs, 
  recsLoading, 
  setRecsLoading 
}) => {
  const [hotspots, setHotspots] = useState([]);
  const [districts, setDistricts] = useState(null);
  const [gridCells, setGridCells] = useState([]);
  const [center, setCenter] = useState([12.9716, 77.5946]);
  const [zoom, setZoom] = useState(11.5);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Layer switches
  const [showGrid, setShowGrid] = useState(true);
  const [showHotspots, setShowHotspots] = useState(true);
  const [showDistricts, setShowDistricts] = useState(true);

  // Map state tracking for optimized lazy loading
  const [currentZoom, setCurrentZoom] = useState(11.5);
  const [currentBounds, setCurrentBounds] = useState(null);

  const handleMapStateChange = (zoomVal, boundsVal) => {
    setCurrentZoom(zoomVal);
    setCurrentBounds(boundsVal);
  };

  useEffect(() => {
    fetchMapData();
  }, [datasetId]);

  const fetchMapData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [hotspotsRes, districtsRes, gridRes] = await Promise.all([
        mapAPI.getHotspots(datasetId),
        mapAPI.getDistricts(datasetId),
        mapAPI.getGrid(datasetId)
      ]);
      
      setHotspots(hotspotsRes.data);
      setDistricts(districtsRes.data);
      setGridCells(gridRes.data);
      
      if (hotspotsRes.data.length > 0) {
        const lats = hotspotsRes.data.map(h => h.latitude);
        const lons = hotspotsRes.data.map(h => h.longitude);
        const avgLat = lats.reduce((sum, val) => sum + val, 0) / lats.length;
        const avgLon = lons.reduce((sum, val) => sum + val, 0) / lons.length;
        setCenter([avgLat, avgLon]);
      }
    } catch (e) {
      console.error("Failed to load map data", e);
      setError("Unable to load spatial layers.");
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'Critical': return '#ef4444';
      case 'High': return '#f97316';
      case 'Medium': return '#eab308';
      default: return '#10b981';
    }
  };

  const districtStyle = (feature) => {
    const cover = feature.properties.land_cover || feature.properties.type || 'Residential';
    let fillColor = '#eab308'; // Default Residential -> Yellow
    let fillOpacity = 0.15;
    let weight = 1.5;
    
    if (cover === 'Park' || cover === 'Forest') {
      fillColor = '#10b981'; // Emerald Green
      fillOpacity = 0.35;
    } else if (cover === 'Water') {
      fillColor = '#3b82f6'; // Vibrant Blue
      fillOpacity = 0.45;
      weight = 2;
    } else if (cover === 'Industrial') {
      fillColor = '#f97316'; // Orange-Red
      fillOpacity = 0.25;
    } else if (cover === 'Commercial') {
      fillColor = '#ec4899'; // Pink/Magenta
      fillOpacity = 0.20;
    }
    
    return {
      fillColor: fillColor,
      weight: weight,
      opacity: 0.8,
      color: cover === 'Water' ? '#2563eb' : '#475569',
      fillOpacity: fillOpacity,
      dashArray: cover === 'Water' ? '0' : '3'
    };
  };

  const getVisibleDistricts = () => {
    if (!districts || !districts.features) return null;
    if (!currentBounds) return districts;
    try {
      const filteredFeatures = districts.features.filter(feature => {
        if (!feature.geometry || !feature.geometry.coordinates) return false;
        const coords = feature.geometry.coordinates[0];
        return coords.some(coord => {
          const lat = coord[1];
          const lon = coord[0];
          return currentBounds.contains([lat, lon]);
        });
      });
      return {
        ...districts,
        features: filteredFeatures
      };
    } catch (e) {
      return districts;
    }
  };

  const onEachDistrict = (feature, layer) => {
    const cover = feature.properties.land_cover || feature.properties.type || 'Residential';
    const tempVal = feature.properties.lst !== undefined && feature.properties.lst !== null ? Number(feature.properties.lst).toFixed(1) : 'N/A';
    const riskLvl = feature.properties.risk_level || 'Medium';
    layer.bindTooltip(
      `<strong>${feature.properties.name}</strong><br/>
       <span class="text-slate-400">Class:</span> <span class="font-bold text-slate-200">${cover}</span><br/>
       <span class="text-slate-400">Temp:</span> <span class="font-bold text-emerald-400">${tempVal}°C</span><br/>
       <span class="text-slate-400">Risk:</span> <span class="font-bold text-rose-400">${riskLvl}</span>`,
      { sticky: true, className: 'glass-panel p-2.5 text-xs font-semibold text-slate-200 border-slate-800 bg-slate-950/90 shadow-2xl' }
    );
  };

  // Click handler to identify the nearest hotspot or grid cell point
  const handleMapClick = async (latlng) => {
    const searchTarget = gridCells.length > 0 ? gridCells : hotspots;
    if (searchTarget.length === 0) return;
    
    let nearest = null;
    let minDist = Infinity;
    
    for (const item of searchTarget) {
      const dist = Math.pow(item.latitude - latlng.lat, 2) + Math.pow(item.longitude - latlng.lng, 2);
      if (dist < minDist) {
        minDist = dist;
        nearest = item;
      }
    }
    
    if (nearest) {
      setSelectedPoint(nearest);
      setRecsLoading(true);
      
      try {
        // Run AI recommendation engine against selected location variables
        const response = await recommendAPI.analyzePoint({
          name: nearest.name,
          latitude: nearest.latitude,
          longitude: nearest.longitude,
          lst: nearest.lst,
          ndvi: nearest.ndvi,
          ndbi: nearest.ndbi,
          land_cover: nearest.land_cover,
          tree_canopy: nearest.tree_canopy,
          population_density: nearest.population_density,
          humidity: nearest.humidity,
          heat_index: nearest.heat_index,
          ward: nearest.ward
        });
        setCustomRecs(response.data);
      } catch (e) {
        console.error("AI engine analysis failed", e);
      } finally {
        setRecsLoading(false);
      }
    }
  };

  // Derive atmospheric attributes from Land Surface Temperature & vegetation index
  const calculateAirTemp = (lst) => lst - 3.5;
  
  const calculateHumidity = (ndvi) => {
    const computed = 40 + ndvi * 50;
    return Math.max(15, Math.min(95, Math.round(computed)));
  };

  const calculateHeatIndex = (tempC, humidity) => {
    const T = tempC * 9/5 + 32; // Fahrenheit
    const R = humidity;
    const hi = 0.5 * (T + 61.0 + ((T - 68.0) * 1.2) + (R * 0.094));
    const hiC = (hi - 32) * 5/9;
    return Math.max(tempC, Math.round(hiC * 10) / 10);
  };

  const getCellRadius = (z) => {
    if (z >= 15) return 32;
    if (z >= 14) return 25;
    if (z >= 13) return 18;
    if (z >= 12) return 12;
    if (z >= 11) return 8;
    return 5;
  };

  const getPriorityBadgeClass = (priority) => {
    switch (priority) {
      case 'Immediate': return 'bg-red-500/10 text-red-400 border-red-500/20';
      case 'Short-Term': return 'bg-orange-500/10 text-orange-400 border-orange-500/20';
      default: return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20';
    }
  };

  const getSeverityBadgeClass = (severity) => {
    switch (severity) {
      case 'Critical': return 'text-red-400 bg-red-950/20 border-red-900/30';
      case 'High': return 'text-orange-400 bg-orange-950/20 border-orange-900/30';
      case 'Moderate': return 'text-yellow-400 bg-yellow-950/20 border-yellow-900/30';
      default: return 'text-emerald-400 bg-emerald-950/20 border-emerald-900/30';
    }
  };

  return (
    <div className="flex-1 flex flex-col gap-6 p-8 max-h-screen overflow-hidden">
      {/* Header Banner */}
      <div className="flex flex-col xl:flex-row justify-between xl:items-center gap-4">
        <div>
          <h2 className="text-3xl font-heading font-extrabold tracking-tight">
            Bengaluru GIS Decision Support System
          </h2>
          <p className="text-slate-400 text-sm mt-1">
            Click anywhere on the map to run spatial interpolation, isolate regional microclimates, and generate dynamic AI recommendations.
          </p>
        </div>
        
        {/* Layers Toggles & Legend Panel */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex gap-1.5 p-1 bg-slate-900/60 border border-slate-800/80 rounded-xl text-[10px] font-bold">
            <button 
              onClick={() => setShowGrid(!showGrid)}
              className={`px-3 py-1.5 rounded-lg transition-all ${showGrid ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'text-slate-500 hover:text-slate-350'}`}
            >
              Grid Heat (IDW)
            </button>
            <button 
              onClick={() => setShowHotspots(!showHotspots)}
              className={`px-3 py-1.5 rounded-lg transition-all ${showHotspots ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'text-slate-500 hover:text-slate-350'}`}
            >
              Vulnerability Pins
            </button>
            <button 
              onClick={() => setShowDistricts(!showDistricts)}
              className={`px-3 py-1.5 rounded-lg transition-all ${showDistricts ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'text-slate-500 hover:text-slate-350'}`}
            >
              Wards &amp; Buffers
            </button>
          </div>

          <div className="flex gap-3 p-2 bg-slate-900/40 border border-slate-800 rounded-xl text-[10px] font-bold">
            <div className="flex items-center gap-1">
              <span className="w-2.5 h-2.5 rounded-full bg-red-500" />
              <span className="text-slate-455">Critical (&gt;41°C)</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="w-2.5 h-2.5 rounded-full bg-orange-500" />
              <span className="text-slate-455">High (35-41°C)</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="w-2.5 h-2.5 rounded-full bg-yellow-500" />
              <span className="text-slate-455">Medium (28-35°C)</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
              <span className="text-slate-455">Low (&lt;28°C)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Split Interface */}
      <div className="flex-1 flex flex-col lg:flex-row gap-6 min-h-0">
        
        {/* Left Side: Interactive Map Container */}
        <div className="flex-1 rounded-2xl overflow-hidden border border-slate-800/80 dark-map relative shadow-2xl min-h-[400px] lg:min-h-0 bg-slate-950/20">
          {loading && (
            <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm z-[1000] flex items-center justify-center gap-3">
              <span className="w-5 h-5 rounded-full border-2 border-emerald-400 border-t-transparent animate-spin" />
              <span className="text-sm font-semibold text-slate-400">Loading spatial layers...</span>
            </div>
          )}

          {error && (
            <div className="absolute inset-0 bg-slate-950/90 backdrop-blur-sm z-[1000] flex flex-col items-center justify-center gap-3 p-6 text-center">
              <ShieldAlert className="w-10 h-10 text-rose-500 animate-pulse" />
              <div>
                <p className="text-sm font-bold text-slate-200">Map Server Offline</p>
                <p className="text-xs text-slate-500 mt-1">{error}</p>
              </div>
              <button 
                onClick={fetchMapData}
                className="mt-2 px-4 py-2 bg-slate-900 border border-slate-800 hover:border-emerald-500/30 text-xs font-semibold text-slate-300 hover:text-emerald-400 rounded-xl transition-all"
              >
                Retry Connection
              </button>
            </div>
          )}

          <MapContainer 
            key={`${center[0]}-${center[1]}-${datasetId}`}
            center={center} 
            zoom={zoom} 
            style={{ height: '100%', width: '100%' }}
            scrollWheelZoom={true}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            {/* Custom Click Listener */}
            <MapClickHandler onClick={handleMapClick} />

            {/* Map State listener to optimize visible cells */}
            <MapStateListener onChange={handleMapStateChange} />

            {/* District Boundaries Wards */}
            {showDistricts && getVisibleDistricts() && (
              <GeoJSON 
                key={`districts-${datasetId}-${getVisibleDistricts().features.length}`}
                data={getVisibleDistricts()} 
                style={districtStyle}
                onEachFeature={onEachDistrict}
              />
            )}

            {/* Pulsing selection circle */}
            {selectedPoint && 
             selectedPoint.latitude !== undefined && selectedPoint.latitude !== null && !isNaN(selectedPoint.latitude) &&
             selectedPoint.longitude !== undefined && selectedPoint.longitude !== null && !isNaN(selectedPoint.longitude) && (
              <CircleMarker
                center={[selectedPoint.latitude, selectedPoint.longitude]}
                radius={24}
                fillColor="transparent"
                color="#38bdf8"
                weight={3}
                dashArray="4"
                className="animate-pulse"
              />
            )}

            {/* Interpolated Grid Heatmap (IDW) */}
            {showGrid && gridCells.map((cell, idx) => {
              if (
                cell.latitude === undefined || cell.latitude === null || isNaN(cell.latitude) ||
                cell.longitude === undefined || cell.longitude === null || isNaN(cell.longitude)
              ) {
                return null;
              }
              const inBounds = () => {
                if (!currentBounds) return true;
                try {
                  return currentBounds.contains([cell.latitude, cell.longitude]);
                } catch (e) {
                  return true;
                }
              };
              if (!inBounds()) return null;
              const radius = getCellRadius(currentZoom);
              return (
                <CircleMarker
                  key={`grid-${idx}`}
                  center={[cell.latitude, cell.longitude]}
                  radius={radius}
                  fillColor={getRiskColor(cell.risk_level)}
                  color={selectedPoint && selectedPoint.latitude === cell.latitude && selectedPoint.longitude === cell.longitude ? "#38bdf8" : "transparent"}
                  weight={1}
                  fillOpacity={0.42}
                  stroke={selectedPoint && selectedPoint.latitude === cell.latitude && selectedPoint.longitude === cell.longitude}
                  eventHandlers={{
                    click: () => handleMapClick({ lat: cell.latitude, lng: cell.longitude })
                  }}
                  className="leaflet-interactive"
                />
              );
            })}

            {/* Hotspots Marker Pins */}
            {showHotspots && hotspots.map((spot) => {
              if (
                spot.latitude === undefined || spot.latitude === null || isNaN(spot.latitude) ||
                spot.longitude === undefined || spot.longitude === null || isNaN(spot.longitude)
              ) {
                return null;
              }
              const isSelected = selectedPoint && selectedPoint.id === spot.id;
              const inBounds = () => {
                if (!currentBounds) return true;
                try {
                  return currentBounds.contains([spot.latitude, spot.longitude]);
                } catch (e) {
                  return true;
                }
              };
              if (!inBounds()) return null;
              return (
                <CircleMarker
                  key={spot.id}
                  center={[spot.latitude, spot.longitude]}
                  radius={isSelected ? 14 : 9 + (spot.lst - 20) / 3}
                  fillColor={getRiskColor(spot.risk_level)}
                  color={isSelected ? '#38bdf8' : getRiskColor(spot.risk_level)}
                  weight={isSelected ? 3 : 1}
                  fillOpacity={isSelected ? 0.75 : 0.4}
                  eventHandlers={{
                    click: () => handleMapClick({ lat: spot.latitude, lng: spot.longitude })
                  }}
                  className="leaflet-interactive"
                />
              );
            })}
          </MapContainer>
        </div>

        {/* Right Side: Environmental Analysis & AI Recommendation Panel */}
        <div className="w-full lg:w-[480px] rounded-2xl border border-slate-800 bg-slate-950/20 glass-panel p-6 flex flex-col gap-6 overflow-y-auto max-h-full">
          
          {selectedPoint ? (
            <div className="flex flex-col gap-6">
              
              {/* Location Header */}
              <div className="border-b border-slate-800 pb-4">
                <div className="flex justify-between items-start gap-2">
                  <div>
                    <h3 className="font-heading font-extrabold text-slate-100 text-lg">
                      {selectedPoint.name}
                    </h3>
                    {selectedPoint.ward && (
                      <p className="text-slate-350 text-xs mt-0.5 font-bold uppercase tracking-wider">
                        {selectedPoint.ward}
                      </p>
                    )}
                    <p className="text-slate-400 text-xs mt-1 font-medium flex items-center gap-1.5">
                      <Compass className="w-3.5 h-3.5 text-slate-500" />
                      Lat: {selectedPoint.latitude.toFixed(4)}, Lon: {selectedPoint.longitude.toFixed(4)}
                    </p>
                  </div>
                  <span className={`px-2.5 py-0.5 border text-[10px] font-extrabold uppercase tracking-wider rounded-full ${getSeverityBadgeClass(selectedPoint.risk_level)}`}>
                    {selectedPoint.risk_level} Risk
                  </span>
                </div>
              </div>

              {/* Environmental Index Diagnostics */}
              <div>
                <h4 className="text-[10px] text-slate-400 font-extrabold uppercase tracking-wider mb-3">
                  Atmospheric &amp; Canopy Readings
                </h4>
                <div className="grid grid-cols-2 gap-3.5 text-xs">
                  
                  <div className="p-3 bg-slate-900/30 border border-slate-850 rounded-xl flex items-center gap-3">
                    <Flame className="w-5 h-5 text-orange-400 flex-shrink-0" />
                    <div>
                      <span className="text-[9px] text-slate-500 block uppercase font-bold">Surface Temp (LST)</span>
                      <span className="font-extrabold text-slate-200 text-sm">{selectedPoint.lst.toFixed(1)}°C</span>
                    </div>
                  </div>

                  <div className="p-3 bg-slate-900/30 border border-slate-850 rounded-xl flex items-center gap-3">
                    <Wind className="w-5 h-5 text-sky-400 flex-shrink-0" />
                    <div>
                      <span className="text-[9px] text-slate-500 block uppercase font-bold">Est Air Temp</span>
                      <span className="font-extrabold text-slate-200 text-sm">{calculateAirTemp(selectedPoint.lst).toFixed(1)}°C</span>
                    </div>
                  </div>

                  <div className="p-3 bg-slate-900/30 border border-slate-850 rounded-xl flex items-center gap-3">
                    <Droplets className="w-5 h-5 text-cyan-400 flex-shrink-0" />
                    <div>
                      <span className="text-[9px] text-slate-500 block uppercase font-bold">Relative Humidity</span>
                      <span className="font-extrabold text-slate-200 text-sm">{calculateHumidity(selectedPoint.ndvi)}%</span>
                    </div>
                  </div>

                  <div className="p-3 bg-slate-900/30 border border-slate-850 rounded-xl flex items-center gap-3">
                    <ShieldAlert className="w-5 h-5 text-rose-400 flex-shrink-0" />
                    <div>
                      <span className="text-[9px] text-slate-500 block uppercase font-bold">Calculated Heat Index</span>
                      <span className="font-extrabold text-slate-200 text-sm">
                        {calculateHeatIndex(calculateAirTemp(selectedPoint.lst), calculateHumidity(selectedPoint.ndvi))}°C
                      </span>
                    </div>
                  </div>

                  <div className="p-3 bg-slate-900/30 border border-slate-850 rounded-xl flex items-center gap-3">
                    <Leaf className="w-5 h-5 text-emerald-400 flex-shrink-0" />
                    <div>
                      <span className="text-[9px] text-slate-500 block uppercase font-bold">Vegetation (NDVI)</span>
                      <span className="font-extrabold text-slate-200 text-sm">{selectedPoint.ndvi.toFixed(3)}</span>
                    </div>
                  </div>

                  <div className="p-3 bg-slate-900/30 border border-slate-850 rounded-xl flex items-center gap-3">
                    <Building className="w-5 h-5 text-blue-400 flex-shrink-0" />
                    <div>
                      <span className="text-[9px] text-slate-500 block uppercase font-bold">Built-up (NDBI)</span>
                      <span className="font-extrabold text-slate-200 text-sm">{selectedPoint.ndbi.toFixed(3)}</span>
                    </div>
                  </div>

                  <div className="p-3 bg-slate-900/30 border border-slate-850 rounded-xl flex items-center gap-3">
                    <Leaf className="w-5 h-5 text-emerald-500 flex-shrink-0" />
                    <div>
                      <span className="text-[9px] text-slate-500 block uppercase font-bold">Vegetation Density</span>
                      <span className="font-extrabold text-slate-200 text-sm">
                        {Math.round(selectedPoint.vegetation_density || Math.max(0, Math.min(100, (selectedPoint.ndvi + 1) * 50)))}%
                      </span>
                    </div>
                  </div>

                  <div className="p-3 bg-slate-900/30 border border-slate-850 rounded-xl flex items-center gap-3">
                    <Building className="w-5 h-5 text-blue-500 flex-shrink-0" />
                    <div>
                      <span className="text-[9px] text-slate-500 block uppercase font-bold">Built-up Density</span>
                      <span className="font-extrabold text-slate-200 text-sm">
                        {Math.round(selectedPoint.built_up_density || Math.max(0, Math.min(100, (selectedPoint.ndbi + 1) * 50)))}%
                      </span>
                    </div>
                  </div>

                  <div className="p-3 bg-slate-900/30 border border-slate-850 rounded-xl flex items-center gap-3">
                    <Leaf className="w-5 h-5 text-emerald-400 flex-shrink-0" />
                    <div>
                      <span className="text-[9px] text-slate-500 block uppercase font-bold">Tree Canopy</span>
                      <span className="font-extrabold text-slate-200 text-sm">
                        {selectedPoint.tree_canopy ? selectedPoint.tree_canopy.toFixed(1) : '0.0'}%
                      </span>
                    </div>
                  </div>

                  <div className="p-3 bg-slate-900/30 border border-slate-850 rounded-xl flex items-center gap-3">
                    <Building className="w-5 h-5 text-indigo-400 flex-shrink-0" />
                    <div>
                      <span className="text-[9px] text-slate-500 block uppercase font-bold">Pop Density</span>
                      <span className="font-extrabold text-slate-200 text-sm">
                        {selectedPoint.population_density ? selectedPoint.population_density.toLocaleString() : '0'}/km²
                      </span>
                    </div>
                  </div>

                  <div className="p-3 bg-slate-900/30 border border-slate-850 rounded-xl flex items-center gap-3">
                    <Activity className="w-5 h-5 text-purple-400 flex-shrink-0" />
                    <div>
                      <span className="text-[9px] text-slate-500 block uppercase font-bold">Zone</span>
                      <span className="font-extrabold text-slate-200 text-sm">{selectedPoint.land_cover || 'Commercial'}</span>
                    </div>
                  </div>

                  <div className="p-3 bg-slate-900/30 border border-slate-850 rounded-xl flex items-center gap-3">
                    <TrendingDown className="w-5 h-5 text-rose-450 flex-shrink-0" />
                    <div>
                      <span className="text-[9px] text-slate-500 block uppercase font-bold">Growth Prediction</span>
                      <span className="font-extrabold text-slate-200 text-sm">
                        +{selectedPoint.growth_5yr ? selectedPoint.growth_5yr.toFixed(2) : (selectedPoint.growth_prediction ? selectedPoint.growth_prediction.toFixed(2) : '1.20')}°C
                      </span>
                    </div>
                  </div>

                  <div className="p-3 bg-slate-900/30 border border-slate-850 rounded-xl flex items-center gap-3">
                    <Flame className="w-5 h-5 text-red-500 flex-shrink-0" />
                    <div>
                      <span className="text-[9px] text-slate-500 block uppercase font-bold">Future Temperature</span>
                      <span className="font-extrabold text-slate-200 text-sm">
                        {((selectedPoint.lst || 0.0) + (selectedPoint.growth_5yr || selectedPoint.growth_prediction || 1.20)).toFixed(1)}°C
                      </span>
                    </div>
                  </div>

                </div>
              </div>

              {/* Dynamic Location-Specific AI Mitigation Strategies */}
              <div className="border-t border-slate-850 pt-5">
                <div className="flex justify-between items-center mb-3">
                  <h4 className="text-[10px] text-slate-400 font-extrabold uppercase tracking-wider">
                    Location-Specific AI Recommendations
                  </h4>
                  <span className="text-[9px] text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 border border-emerald-500/15 rounded-md uppercase">
                    Heuristics Triggered
                  </span>
                </div>

                {recsLoading ? (
                  <div className="py-12 flex flex-col items-center justify-center gap-2">
                    <span className="w-5 h-5 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin" />
                    <span className="text-slate-500 text-[10px]">Evaluating thermal offsets...</span>
                  </div>
                ) : (
                  <div className="flex flex-col gap-3.5">
                    {customRecs.map((rec, i) => (
                      <div 
                        key={i} 
                        className="p-4 rounded-xl border border-slate-800 bg-slate-950/40 hover:border-slate-700 transition-all flex flex-col gap-2.5"
                      >
                        <div className="flex justify-between items-start gap-1">
                          <span className="font-bold text-slate-200 text-xs">
                            {rec.strategy_name}
                          </span>
                          <span className={`px-2 py-0.5 border text-[8px] font-extrabold uppercase tracking-wider rounded-md ${getPriorityBadgeClass(rec.priority_level)}`}>
                            {rec.priority_level}
                          </span>
                        </div>

                        {/* Mitigation Logic */}
                        <div className="text-[11px] text-slate-400 leading-relaxed font-medium">
                          <span className="text-slate-500 font-extrabold uppercase text-[8px] mr-1.5">Reason:</span>
                          {rec.reason}
                        </div>

                        {/* Impact Indicators */}
                        <div className="grid grid-cols-3 gap-2 bg-slate-900/30 p-2.5 border border-slate-900 rounded-lg text-[10px] font-bold">
                          <div className="flex flex-col gap-0.5">
                            <span className="text-[8px] text-slate-500 uppercase tracking-wider font-semibold flex items-center gap-1">
                              <TrendingDown className="w-3 h-3 text-emerald-400" />
                              Cooling Est
                            </span>
                            <span className="text-slate-200">-{rec.temp_reduction.toFixed(1)}°C</span>
                          </div>

                          <div className="flex flex-col gap-0.5">
                            <span className="text-[8px] text-slate-500 uppercase tracking-wider font-semibold flex items-center gap-1">
                              <DollarSign className="w-3 h-3 text-orange-400" />
                              Cost
                            </span>
                            <span className="text-slate-200 uppercase">{rec.cost_level}</span>
                          </div>

                          <div className="flex flex-col gap-0.5">
                            <span className="text-[8px] text-slate-500 uppercase tracking-wider font-semibold flex items-center gap-1">
                              <Percent className="w-3 h-3 text-cyan-400" />
                              Confidence
                            </span>
                            <span className="text-slate-200">{rec.confidence_score.toFixed(0)}%</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-center p-8 gap-3 text-slate-500">
              <Activity className="w-12 h-12 text-slate-700 border border-slate-800/80 p-3 rounded-2xl bg-slate-900/30" />
              <div>
                <h4 className="text-sm font-bold text-slate-300">No Location Selected</h4>
                <p className="text-xs text-slate-500 mt-1 max-w-[280px] leading-relaxed">
                  Interactive GIS Mode Active. Click anywhere on the map interface or select individual hotspot markers to run localized diagnostics.
                </p>
              </div>
            </div>
          )}

        </div>

      </div>
    </div>
  );
};

export default HeatMap;
