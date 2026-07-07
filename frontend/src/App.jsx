import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import UploadPanel from './components/UploadPanel';
import HeatMap from './components/HeatMap';
import Recommendations from './components/Recommendations';
import AIAssistant from './components/AIAssistant';
import Reports from './components/Reports';
import Settings from './components/Settings';
import { dashboardAPI } from './utils/api';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [datasetId, setDatasetId] = useState(null);
  const [datasetName, setDatasetName] = useState('Loading...');
  const [summary, setSummary] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  
  // Shared global context state for GIS point selection
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [locationRecs, setLocationRecs] = useState([]);
  const [recsLoading, setRecsLoading] = useState(false);

  useEffect(() => {
    fetchSummary();
  }, [datasetId]);

  const fetchSummary = async () => {
    try {
      const response = await dashboardAPI.getSummary(datasetId);
      setSummary(response.data);
      if (response.data.dataset_info) {
        setDatasetName(response.data.dataset_info.filename);
        setDatasetId(response.data.dataset_info.id);
        setIsProcessing(false);
      }
    } catch (e) {
      console.error("Failed to load dashboard summary", e);
    }
  };

  const handleUploadSuccess = (newDatasetId) => {
    if (newDatasetId) {
      setIsProcessing(true);
      setDatasetId(newDatasetId);
      // Reset selected location when a new file is uploaded
      setSelectedLocation(null);
      setLocationRecs([]);
      
      const interval = setInterval(async () => {
        try {
          const res = await dashboardAPI.getSummary(newDatasetId);
          if (res.data.dataset_info && res.data.dataset_info.id !== 0) {
            fetchSummary();
            clearInterval(interval);
          }
        } catch (err) {
          console.error("Polling summary failed", err);
        }
      }, 3000);
    } else {
      setDatasetId(null);
      setSelectedLocation(null);
      setLocationRecs([]);
    }
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard summary={summary} setActiveTab={setActiveTab} selectedLocation={selectedLocation} />;
      case 'upload':
        return <UploadPanel onUploadSuccess={handleUploadSuccess} />;
      case 'heatmap':
        return (
          <HeatMap 
            datasetId={datasetId} 
            selectedPoint={selectedLocation}
            setSelectedPoint={setSelectedLocation}
            customRecs={locationRecs}
            setCustomRecs={setLocationRecs}
            recsLoading={recsLoading}
            setRecsLoading={setRecsLoading}
          />
        );
      case 'recommendations':
        return (
          <Recommendations 
            datasetId={datasetId} 
            summary={summary} 
            selectedLocation={selectedLocation}
            locationRecs={locationRecs}
            recsLoading={recsLoading}
            setActiveTab={setActiveTab}
          />
        );
      case 'assistant':
        return <AIAssistant selectedLocation={selectedLocation} />;
      case 'reports':
        return <Reports datasetId={datasetId} selectedLocation={selectedLocation} />;
      case 'settings':
        return <Settings onUploadSuccess={handleUploadSuccess} datasetId={datasetId} />;
      default:
        return <Dashboard summary={summary} setActiveTab={setActiveTab} selectedLocation={selectedLocation} />;
    }
  };

  // Page slide animations
  const pageVariants = {
    initial: { opacity: 0, x: 15 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -15 }
  };

  return (
    <div className="flex w-screen h-screen bg-slate-950 text-slate-100 overflow-hidden font-sans">
      {/* Side Navigation Panel */}
      <Sidebar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        datasetName={datasetName}
        isProcessing={isProcessing}
      />

      {/* Viewport Frame */}
      <div className="flex-1 flex flex-col min-w-0 bg-[#090d16]/30 relative overflow-hidden">
        {/* Glassmorphic decorative ambient lighting blobs */}
        <div className="absolute top-[-20%] left-[-10%] w-[500px] h-[500px] bg-emerald-500/10 rounded-full blur-[120px] pointer-events-none" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[600px] h-[600px] bg-cyan-500/5 rounded-full blur-[150px] pointer-events-none" />

        <div className="relative z-10 flex-1 flex flex-col min-h-0">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial="initial"
              animate="animate"
              exit="exit"
              variants={pageVariants}
              transition={{ duration: 0.22, ease: 'easeInOut' }}
              className="flex-1 flex flex-col min-h-0"
            >
              {renderContent()}
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}

export default App;
