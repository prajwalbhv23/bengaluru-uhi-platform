import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Download, 
  History, 
  ArrowRight,
  TrendingDown,
  Activity,
  Layers
} from 'lucide-react';
import { historyAPI, reportAPI } from '../utils/api';

const Reports = ({ datasetId }) => {
  const [history, setHistory] = useState([]);
  const [downloadingId, setDownloadingId] = useState(null);

  useEffect(() => {
    fetchHistory();
  }, [datasetId]);

  const fetchHistory = async () => {
    try {
      const response = await historyAPI.getHistory();
      setHistory(response.data.filter(d => d.status === 'Processed'));
    } catch (e) {
      console.error("Failed to load report history", e);
    }
  };

  const handleDownload = async (id, filename) => {
    setDownloadingId(id);
    try {
      const response = await reportAPI.downloadReport(id);
      
      // Determine extension based on content-type
      const contentType = response.headers['content-type'];
      const ext = contentType && contentType.includes('text') ? 'txt' : 'pdf';
      const type = contentType || 'application/pdf';
      
      const blob = new Blob([response.data], { type });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `UHI_Executive_Report_${filename.split('.')[0]}.${ext}`);
      
      document.body.appendChild(link);
      link.click();
      
      // Clean up
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (e) {
      alert("Failed to download PDF report. Ensure backend PDF dependencies are set up.");
    } finally {
      setDownloadingId(null);
    }
  };

  return (
    <div className="flex-1 flex flex-col gap-6 overflow-y-auto p-8 max-h-screen">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-heading font-extrabold tracking-tight">
          Executive Reports center
        </h2>
        <p className="text-slate-400 text-sm mt-1">
          Compile and download professional, publication-ready PDF reports summarizing UHI hazard layers and recommendations.
        </p>
      </div>

      {/* Report Info Banner */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {[
          { label: 'Executive Summaries', desc: 'Auto-compiled summaries detailing hotspot counts, high-risk zones, and cooling strategies.', icon: FileText, color: 'text-emerald-400 border-emerald-500/10 bg-emerald-500/5' },
          { label: 'Spatial Metrics Grid', desc: 'Aggregated summaries showing peak surface temperatures, average NDVI, and built-up indices.', icon: Layers, color: 'text-sky-400 border-sky-500/10 bg-sky-500/5' },
          { label: 'Carbon Reduction', desc: 'Estimates of environmental offsets, building energy saving ratios, and cost layouts.', icon: TrendingDown, color: 'text-orange-400 border-orange-500/10 bg-orange-500/5' },
        ].map((item, i) => (
          <div key={i} className={`p-5 rounded-2xl border flex flex-col gap-3 ${item.color}`}>
            <item.icon className="w-6 h-6" />
            <h3 className="text-sm font-bold text-slate-100">{item.label}</h3>
            <p className="text-[11px] text-slate-400 leading-relaxed font-medium">{item.desc}</p>
          </div>
        ))}
      </div>

      {/* History / Downloads Database */}
      <div className="flex-1 flex flex-col gap-3.5 mt-2 min-h-0">
        <div className="flex items-center gap-2 text-xs font-bold text-slate-300">
          <History className="w-4.5 h-4.5 text-emerald-400" />
          <span>REPORT ARCHIVE FOR PROCESSED RUNS</span>
        </div>

        <div className="flex-1 rounded-2xl glass-panel overflow-hidden border border-slate-800/80 flex flex-col min-h-0">
          <div className="overflow-y-auto flex-1">
            <table className="w-full border-collapse text-left text-xs">
              <thead className="bg-slate-900/60 text-slate-400 font-semibold border-b border-slate-800 sticky top-0 z-10">
                <tr>
                  <th className="p-4">Reference File</th>
                  <th className="p-4">Hotspots Count</th>
                  <th className="p-4">Process Date</th>
                  <th className="p-4 text-right">Download Report</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-850 font-medium">
                {history.length > 0 ? (
                  history.map((item) => (
                    <tr key={item.id} className="hover:bg-slate-900/35 transition-colors">
                      <td className="p-4 flex items-center gap-3 text-slate-200">
                        <FileText className="w-5 h-5 text-emerald-400" />
                        <span>{item.filename}</span>
                      </td>
                      <td className="p-4 text-slate-300">
                        {item.records_count} locations
                      </td>
                      <td className="p-4 text-slate-400">
                        {new Date(item.upload_time).toLocaleString()}
                      </td>
                      <td className="p-4 text-right">
                        <button
                          onClick={() => handleDownload(item.id, item.filename)}
                          disabled={downloadingId !== null}
                          className="inline-flex items-center gap-2 px-4 py-2 bg-slate-900 border border-slate-800 hover:border-emerald-500/30 hover:bg-slate-900 text-xs font-semibold text-slate-300 hover:text-emerald-400 rounded-xl transition-all disabled:opacity-50"
                        >
                          {downloadingId === item.id ? (
                            <span className="w-3.5 h-3.5 rounded-full border border-emerald-400 border-t-transparent animate-spin" />
                          ) : (
                            <Download className="w-3.5 h-3.5" />
                          )}
                          <span>Download PDF</span>
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="4" className="p-10 text-center text-slate-500">
                      No reports generated yet. Upload a dataset to compile PDF reports.
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

export default Reports;
