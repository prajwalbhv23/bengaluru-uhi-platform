import React from 'react';
import { motion } from 'framer-motion';
import { 
  LayoutDashboard, 
  Upload, 
  Map, 
  Sparkles, 
  FileText, 
  Settings as SettingsIcon,
  MessageSquare,
  Activity,
  ThermometerSun
} from 'lucide-react';

const Sidebar = ({ activeTab, setActiveTab, datasetName, isProcessing }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'heatmap', label: 'GIS Heat Map', icon: Map },
    { id: 'recommendations', label: 'AI Recommendations', icon: Sparkles },
    { id: 'assistant', label: 'AI Assistant', icon: MessageSquare },
    { id: 'reports', label: 'Reports', icon: FileText },
    { id: 'settings', label: 'Settings', icon: SettingsIcon },
  ];

  return (
    <div className="w-72 h-screen glass-panel flex flex-col justify-between p-6 border-r border-slate-800">
      {/* Brand Logo Section */}
      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-gradient-to-br from-emerald-500 to-cyan-500 rounded-xl shadow-lg shadow-emerald-500/20">
            <ThermometerSun className="w-7 h-7 text-slate-950 font-bold" />
          </div>
          <div>
            <h1 className="font-heading text-base font-extrabold tracking-tight bg-gradient-to-r from-emerald-400 via-cyan-400 to-sky-400 bg-clip-text text-transparent">
              BENGALURU UHI
            </h1>
            <p className="text-[9px] text-slate-400 font-medium tracking-wider uppercase">
              Climate Intelligence Platform
            </p>
          </div>
        </div>
        <div className="h-[1px] w-full bg-gradient-to-r from-transparent via-slate-700 to-transparent mt-4" />
      </div>

      {/* Menu Options */}
      <nav className="flex-1 flex flex-col gap-1.5 mt-8">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className="relative w-full flex items-center gap-3.5 px-4 py-3 rounded-xl text-sm font-medium transition-all group overflow-hidden"
            >
              {isActive && (
                <motion.div
                  layoutId="active-nav-pill"
                  className="absolute inset-0 bg-gradient-to-r from-emerald-500/15 to-cyan-500/10 border-l-[3px] border-emerald-500"
                  transition={{ type: "spring", stiffness: 380, damping: 30 }}
                />
              )}
              
              <Icon className={`w-5 h-5 transition-transform duration-300 group-hover:scale-110 ${
                isActive ? 'text-emerald-400' : 'text-slate-400 group-hover:text-slate-200'
              }`} />
              
              <span className={`z-10 transition-colors duration-300 ${
                isActive ? 'text-slate-100 font-semibold' : 'text-slate-400 group-hover:text-slate-200'
              }`}>
                {item.label}
              </span>
            </button>
          );
        })}
      </nav>

      {/* Active Dataset Status Widget */}
      <div className="flex flex-col gap-3.5 p-4 rounded-2xl bg-slate-900/40 border border-slate-800/80">
        <div className="flex items-center gap-2">
          <Activity className={`w-4 h-4 ${isProcessing ? 'text-orange-400 animate-pulse' : 'text-emerald-400 animate-spin-slow'}`} />
          <span className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold">
            System State
          </span>
        </div>
        <div>
          <p className="text-xs font-semibold text-slate-200 truncate" title={datasetName}>
            {datasetName}
          </p>
          <div className="flex items-center gap-1.5 mt-1.5">
            <span className={`w-2 h-2 rounded-full ${isProcessing ? 'bg-orange-500 animate-ping' : 'bg-emerald-500'}`} />
            <span className="text-[10px] text-slate-400 font-medium">
              {isProcessing ? 'Processing Imagery' : 'Model Synchronized'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
