import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Upload, 
  FileText, 
  Trash2, 
  CheckCircle, 
  XCircle, 
  Loader2, 
  AlertCircle,
  FileSpreadsheet,
  FileJson,
  FileImage
} from 'lucide-react';
import { uploadAPI, historyAPI } from '../utils/api';

const UploadPanel = ({ onUploadSuccess }) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [history, setHistory] = useState([]);
  const fileInputRef = useRef(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await historyAPI.getHistory();
      setHistory(response.data);
    } catch (e) {
      console.error("Failed to load upload history", e);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      await uploadFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = async (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      await uploadFile(e.target.files[0]);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  const uploadFile = async (file) => {
    const filename = file.name;
    const ext = filename.split('.').pop().lowerCase || filename.split('.').pop().toLowerCase();
    
    const allowed = ["csv", "geojson", "tif", "tiff", "geotiff", "png", "jpg", "jpeg"];
    if (!allowed.includes(ext)) {
      setError(`Format .${ext} not supported. Use GeoTIFF, GeoJSON, CSV, PNG, or JPG.`);
      setTimeout(() => setError(null), 5000);
      return;
    }

    setUploading(true);
    setProgress(0);
    setError(null);
    setSuccess(null);

    try {
      const response = await uploadAPI.upload(file, (progressEvent) => {
        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        setProgress(percent);
      });

      setSuccess(`Dataset "${filename}" is being processed by the ML engine...`);
      onUploadSuccess(response.data.dataset_id);
      fetchHistory();
      
      // Clear success notification
      setTimeout(() => setSuccess(null), 6000);
    } catch (e) {
      setError(e.response?.data?.detail || "Upload failed. Verify backend server connectivity.");
    } finally {
      setUploading(false);
      setProgress(0);
    }
  };

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    if (!window.confirm("Delete this dataset and all associated predictions?")) return;
    
    try {
      await historyAPI.deleteDataset(id);
      fetchHistory();
      onUploadSuccess(null); // reload summary
    } catch (e) {
      alert("Failed to delete dataset.");
    }
  };

  const getFileIcon = (fileType) => {
    const type = fileType.toLowerCase();
    if (type === 'csv') return <FileSpreadsheet className="w-5 h-5 text-emerald-400" />;
    if (type === 'geojson') return <FileJson className="w-5 h-5 text-sky-400" />;
    if (['tif', 'tiff', 'geotiff'].includes(type)) return <FileImage className="w-5 h-5 text-orange-400" />;
    return <FileText className="w-5 h-5 text-purple-400" />;
  };

  return (
    <div className="flex-1 flex flex-col gap-6 overflow-y-auto p-8 max-h-screen">
      <div>
        <h2 className="text-3xl font-heading font-extrabold tracking-tight">
          Spatial Dataset Uploader
        </h2>
        <p className="text-slate-400 text-sm mt-1">
          Upload satellite imagery, sensor coordinates, or district boundaries to train the microclimate ML models.
        </p>
      </div>

      {/* Drag & Drop Box */}
      <div 
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={triggerFileInput}
        className={`w-full py-14 border-2 border-dashed rounded-2xl flex flex-col items-center justify-center gap-4 cursor-pointer transition-all duration-300 ${
          dragActive 
            ? 'border-emerald-400 bg-emerald-500/5 shadow-inner' 
            : 'border-slate-800 bg-slate-900/10 hover:border-slate-700 hover:bg-slate-900/30'
        }`}
      >
        <input 
          ref={fileInputRef}
          type="file" 
          className="hidden" 
          onChange={handleChange}
          accept=".csv,.geojson,.tif,.tiff,.png,.jpg,.jpeg"
        />

        <div className={`p-4 rounded-full bg-slate-900 border border-slate-800 shadow-md ${dragActive ? 'animate-bounce' : ''}`}>
          <Upload className="w-8 h-8 text-emerald-400" />
        </div>

        <div className="text-center">
          <p className="text-sm font-semibold text-slate-200">
            Drag &amp; drop spatial dataset file here, or <span className="text-emerald-400 underline">browse computer</span>
          </p>
          <p className="text-xs text-slate-500 mt-2 font-medium">
            Supports GeoTIFF (.tif, .tiff), GeoJSON (.geojson), CSV, PNG, JPG (Max 50MB)
          </p>
        </div>
      </div>

      {/* Upload Progress & Alert Indicators */}
      <AnimatePresence>
        {uploading && (
          <motion.div 
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 flex flex-col gap-3"
          >
            <div className="flex justify-between items-center text-xs font-semibold">
              <span className="flex items-center gap-2 text-slate-300">
                <Loader2 className="w-4 h-4 text-emerald-400 animate-spin" />
                Uploading and parsing bands...
              </span>
              <span className="text-emerald-400">{progress}%</span>
            </div>
            <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800">
              <div 
                className="bg-gradient-to-r from-emerald-500 to-cyan-500 h-full rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </motion.div>
        )}

        {error && (
          <motion.div 
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-xs flex items-center gap-3"
          >
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <p className="font-medium">{error}</p>
          </motion.div>
        )}

        {success && (
          <motion.div 
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs flex items-center gap-3"
          >
            <CheckCircle className="w-5 h-5 flex-shrink-0" />
            <p className="font-medium">{success}</p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Dataset History Table */}
      <div className="flex-1 flex flex-col gap-3.5 mt-2 min-h-0">
        <h3 className="text-base font-bold text-slate-200">
          Geospatial Dataset Database
        </h3>
        
        <div className="flex-1 rounded-2xl glass-panel overflow-hidden border border-slate-800/80 flex flex-col min-h-0">
          <div className="overflow-y-auto flex-1">
            <table className="w-full border-collapse text-left text-xs">
              <thead className="bg-slate-900/60 text-slate-400 font-semibold border-b border-slate-800 sticky top-0 z-10">
                <tr>
                  <th className="p-4">Dataset Name</th>
                  <th className="p-4">File Type</th>
                  <th className="p-4">Upload Date</th>
                  <th className="p-4">Records Count</th>
                  <th className="p-4">Processing Status</th>
                  <th className="p-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-850 font-medium">
                {history.length > 0 ? (
                  history.map((item) => (
                    <tr 
                      key={item.id} 
                      className="hover:bg-slate-900/35 transition-colors cursor-pointer group"
                      onClick={() => onUploadSuccess(item.id)}
                    >
                      <td className="p-4 flex items-center gap-3 max-w-xs truncate text-slate-200">
                        {getFileIcon(item.file_type)}
                        <span className="truncate" title={item.filename}>{item.filename}</span>
                      </td>
                      <td className="p-4 font-mono text-[10px] text-slate-400 uppercase">
                        {item.file_type}
                      </td>
                      <td className="p-4 text-slate-400">
                        {new Date(item.upload_time).toLocaleString()}
                      </td>
                      <td className="p-4 text-slate-300">
                        {item.records_count || '-'}
                      </td>
                      <td className="p-4">
                        <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-semibold tracking-wider uppercase border ${
                          item.status === 'Processed' 
                            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' 
                            : item.status === 'Processing'
                            ? 'bg-orange-500/10 text-orange-400 border-orange-500/20 animate-pulse'
                            : 'bg-red-500/10 text-red-400 border-red-500/20'
                        }`}>
                          {item.status}
                        </span>
                      </td>
                      <td className="p-4 text-right">
                        <button
                          onClick={(e) => handleDelete(item.id, e)}
                          className="p-2 text-slate-500 hover:text-red-400 rounded-lg hover:bg-slate-800 transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="6" className="p-10 text-center text-slate-500">
                      No datasets uploaded yet. Standard climate samples are active by default.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadPanel;
