import React from 'react';
import { motion } from 'framer-motion';
import { Bar, Doughnut, Line } from 'react-chartjs-2';
import { 
  Chart as ChartJS, 
  registerables 
} from 'chart.js';
import { 
  Thermometer, 
  Leaf, 
  AlertTriangle, 
  Flame, 
  Settings as ToolsIcon, 
  Wind,
  Layers,
  ArrowUpRight
} from 'lucide-react';

ChartJS.register(...registerables);

const Dashboard = ({ summary, setActiveTab, selectedLocation }) => {
  const kpis = summary?.kpis || {
    avg_temp: 34.2,
    max_temp: 46.5,
    avg_ndvi: 0.285,
    avg_ndbi: 0.324,
    hotspots_found: 36,
    high_risk_zones: 14,
    mitigation_projects: 48,
    carbon_reduction: 820.4
  };

  const datasetInfo = summary?.dataset_info || {
    filename: 'Sample_Metro_Area_Sentinel2.tif'
  };

  const chartData = summary?.charts || {
    land_cover: [],
    risk_levels: [],
    temp_trend: []
  };

  // 1. Land Cover Chart
  const landCoverChartData = {
    labels: chartData.land_cover.map(item => item.name),
    datasets: [{
      data: chartData.land_cover.map(item => item.value),
      backgroundColor: [
        '#38bdf8', // sky-400 (Residential)
        '#fb7185', // rose-400 (Commercial)
        '#f59e0b', // amber-500 (Industrial)
        '#10b981', // emerald-500 (Park)
        '#6366f1'  // indigo-500 (Water)
      ],
      borderWidth: 0,
    }]
  };

  // 2. Risk Levels Chart
  const riskLevelsChartData = {
    labels: chartData.risk_levels.map(item => item.name),
    datasets: [{
      label: 'Zones Count',
      data: chartData.risk_levels.map(item => item.value),
      backgroundColor: [
        '#10b981', // Low -> Emerald
        '#eab308', // Medium -> Yellow
        '#f97316', // High -> Orange
        '#ef4444'  // Critical -> Red
      ],
      borderRadius: 6,
    }]
  };

  // 3. Temperature & NDVI Trend Chart
  const tempTrendChartData = {
    labels: chartData.temp_trend.map(item => item.name),
    datasets: [
      {
        type: 'line',
        label: 'Surface Temp (°C)',
        data: chartData.temp_trend.map(item => item.temp),
        borderColor: '#f97316',
        backgroundColor: 'rgba(249, 115, 22, 0.1)',
        yAxisID: 'y',
        fill: true,
        tension: 0.4,
        borderWidth: 2,
      },
      {
        type: 'line',
        label: 'NDVI (Vegetation Index)',
        data: chartData.temp_trend.map(item => item.ndvi),
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.05)',
        yAxisID: 'y1',
        tension: 0.4,
        borderWidth: 2,
        borderDash: [5, 5],
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: { color: '#94a3b8', font: { family: 'Inter', size: 11 } }
      }
    },
    scales: {
      x: { grid: { color: 'rgba(255, 255, 255, 0.04)' }, ticks: { color: '#94a3b8' } },
      y: { grid: { color: 'rgba(255, 255, 255, 0.04)' }, ticks: { color: '#94a3b8' } }
    }
  };

  const doubleAxisOptions = {
    ...chartOptions,
    scales: {
      x: { grid: { color: 'rgba(255, 255, 255, 0.04)' }, ticks: { color: '#94a3b8' } },
      y: {
        type: 'linear',
        display: true,
        position: 'left',
        grid: { color: 'rgba(255, 255, 255, 0.04)' },
        ticks: { color: '#94a3b8' },
        title: { display: true, text: 'Temperature (°C)', color: '#f97316' }
      },
      y1: {
        type: 'linear',
        display: true,
        position: 'right',
        grid: { drawOnChartArea: false },
        ticks: { color: '#94a3b8' },
        title: { display: true, text: 'NDVI Value', color: '#10b981' }
      }
    }
  };

  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: (i) => ({
      opacity: 1,
      y: 0,
      transition: { delay: i * 0.05, type: 'spring', stiffness: 100 }
    })
  };

  return (
    <div className="flex-1 flex flex-col gap-6 overflow-y-auto p-8 max-h-screen">
      {/* Header Banner */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-heading font-extrabold tracking-tight">
            Bengaluru Climate Intelligence Overview
          </h2>
          <p className="text-slate-400 text-sm mt-1">
            Analyzing geospatial metrics for: <span className="text-emerald-400 font-semibold">{datasetInfo.filename}</span>
          </p>
        </div>
        
        <button 
          onClick={() => setActiveTab('upload')}
          className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-emerald-500 to-cyan-500 text-slate-950 font-semibold rounded-xl hover:shadow-lg hover:shadow-emerald-500/25 transition-all"
        >
          <span>Upload Image</span>
          <ArrowUpRight className="w-4 h-4" />
        </button>
      </div>

      {/* Selected Location Context Alert */}
      {selectedLocation && (
        <div className="p-4 rounded-xl border border-sky-500/20 bg-sky-950/10 flex items-center justify-between text-xs">
          <div className="flex items-center gap-3">
            <span className="w-2 h-2 rounded-full bg-sky-400 animate-ping" />
            <p className="text-slate-300 font-medium">
              Active Context: <b className="text-white font-bold">{selectedLocation.name}</b> selected on the map. Surface Temp: <b className="text-orange-400 font-extrabold">{selectedLocation.lst.toFixed(1)}°C</b>.
            </p>
          </div>
          <button 
            onClick={() => setActiveTab('recommendations')}
            className="text-sky-400 hover:text-sky-300 font-semibold flex items-center gap-1"
          >
            <span>View Local AI Recommendations</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        {[
          { label: 'Avg Surface Temp', val: `${kpis.avg_temp}°C`, icon: Thermometer, color: 'from-orange-500/20 to-red-500/10 border-orange-500/20 text-orange-400' },
          { label: 'Highest Hotspot', val: `${kpis.max_temp}°C`, icon: Flame, color: 'from-red-600/20 to-orange-500/10 border-red-500/20 text-red-400' },
          { label: 'UHI Intensity', val: `${kpis.uhi_intensity || '20.7'}°C`, icon: Layers, color: 'from-blue-500/20 to-indigo-500/10 border-blue-500/20 text-blue-400' },
          { label: 'Detected Hotspots', val: kpis.hotspots_found, icon: AlertTriangle, color: 'from-amber-500/20 to-yellow-500/10 border-amber-500/20 text-amber-400' },
          { label: 'Water Body Coverage', val: `${kpis.water_body_coverage || '2.5'}%`, icon: Wind, color: 'from-teal-500/20 to-emerald-500/10 border-teal-500/20 text-teal-400' },
          { label: 'Vegetation Canopy (NDVI)', val: kpis.avg_ndvi, icon: Leaf, color: 'from-emerald-500/20 to-teal-500/10 border-emerald-500/20 text-emerald-400' },
          { label: 'Mitigation Projects', val: kpis.mitigation_projects, icon: ToolsIcon, color: 'from-cyan-500/20 to-sky-500/10 border-cyan-500/20 text-cyan-400' },
          { label: 'Carbon Reduction', val: `${kpis.carbon_reduction} t/yr`, icon: Wind, color: 'from-rose-500/20 to-red-600/10 border-rose-500/20 text-rose-400' },
        ].map((card, i) => (
          <motion.div
            key={card.label}
            custom={i}
            initial="hidden"
            animate="visible"
            variants={cardVariants}
            className={`p-5 rounded-2xl bg-gradient-to-br border ${card.color} glass-panel flex justify-between items-center`}
          >
            <div>
              <p className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold">
                {card.label}
              </p>
              <h3 className="text-2xl font-bold font-heading mt-1.5 text-white">
                {card.val}
              </h3>
            </div>
            <div className={`p-3 rounded-xl bg-slate-950/40 border border-white/5 ${card.text}`}>
              <card.icon className="w-6 h-6" />
            </div>
          </motion.div>
        ))}
      </div>

      {/* Charts Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-2">
        {/* Land Surface Temperature & NDVI Correlations */}
        <div className="lg:col-span-2 p-6 rounded-2xl glass-panel flex flex-col gap-4 h-96">
          <h4 className="text-base font-bold text-slate-200">
            LST &amp; NDVI Environmental Dynamics
          </h4>
          <div className="flex-1 min-h-0">
            {chartData.temp_trend.length > 0 ? (
              <Line data={tempTrendChartData} options={doubleAxisOptions} />
            ) : (
              <div className="h-full flex items-center justify-center text-slate-500">No chart data</div>
            )}
          </div>
        </div>

        {/* Land Cover Classification */}
        <div className="p-6 rounded-2xl glass-panel flex flex-col gap-4 h-96">
          <h4 className="text-base font-bold text-slate-200">
            Urban Cover Typology Breakdown
          </h4>
          <div className="flex-1 min-h-0">
            {chartData.land_cover.length > 0 ? (
              <Doughnut data={landCoverChartData} options={{ ...chartOptions, cutOut: '70%' }} />
            ) : (
              <div className="h-full flex items-center justify-center text-slate-500">No chart data</div>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Risk Vulnerability Profile */}
        <div className="p-6 rounded-2xl glass-panel flex flex-col gap-4 h-80">
          <h4 className="text-base font-bold text-slate-200">
            Hotspot Risk Classification Count
          </h4>
          <div className="flex-1 min-h-0">
            {chartData.risk_levels.length > 0 ? (
              <Bar data={riskLevelsChartData} options={chartOptions} />
            ) : (
              <div className="h-full flex items-center justify-center text-slate-500">No chart data</div>
            )}
          </div>
        </div>

        {/* Spatial Heat Summary Insights card */}
        <div className="lg:col-span-2 p-6 rounded-2xl glass-panel flex flex-col justify-between h-80">
          <div>
            <h4 className="text-base font-bold text-slate-200">
              Bengaluru UHI Climate Diagnostic Analysis
            </h4>
            <p className="text-slate-400 text-xs mt-2 leading-relaxed">
              Based on Bengaluru's processed raster band layers, the active dataset points exhibit a strong negative correlation 
              between canopy density (NDVI) and thermal retention (LST). Commercial zones like Whitefield and industrial hubs like Peenya contain highly positive NDBI values, 
              acting as massive heat sinks. 
            </p>
            <div className="grid grid-cols-2 gap-4 mt-5">
              <div className="p-3.5 bg-slate-900/50 rounded-xl border border-slate-800">
                <span className="text-[10px] text-slate-400 block uppercase tracking-wider font-semibold">
                  Primary Threat Area
                </span>
                <span className="text-sm font-bold text-red-400 mt-1 block">
                  Peenya / Whitefield
                </span>
              </div>
              <div className="p-3.5 bg-slate-900/50 rounded-xl border border-slate-800">
                <span className="text-[10px] text-slate-400 block uppercase tracking-wider font-semibold">
                  Peak Target Cooling
                </span>
                <span className="text-sm font-bold text-emerald-400 mt-1 block">
                  -5.5°C Surface Temp
                </span>
              </div>
            </div>
          </div>
          
          <div className="border-t border-slate-800/80 pt-4 flex justify-between items-center text-xs">
            <span className="text-slate-500">
              Powered by Random Forest Climate Regressor
            </span>
            <button 
              onClick={() => setActiveTab('heatmap')}
              className="text-emerald-400 hover:text-emerald-300 font-semibold flex items-center gap-1"
            >
              <span>View GIS Spatial Layout</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
