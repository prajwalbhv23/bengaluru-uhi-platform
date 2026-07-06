import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Send, 
  Trash2, 
  Bot, 
  User, 
  Sparkles,
  HelpCircle,
  AlertCircle
} from 'lucide-react';
import { chatAPI } from '../utils/api';

const AIAssistant = ({ selectedLocation }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const chatBottomRef = useRef(null);

  const suggestedPrompts = selectedLocation 
    ? [
        `Why is it hot here in ${selectedLocation.name.split(' ')[0]}?`,
        `What mitigation actions work for ${selectedLocation.name.split(' ')[0]}?`,
        "What are the hottest regions in Bengaluru?",
        "Show dataset stats"
      ]
    : [
        "What are the hottest regions in Bengaluru?",
        "Suggest mitigation strategies for Whitefield.",
        "Why is Electronic City warmer than Cubbon Park?",
        "Why is this hotspot dangerous?",
        "Show dataset stats"
      ];

  useEffect(() => {
    loadChatHistory();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const loadChatHistory = async () => {
    try {
      const response = await chatAPI.getHistory();
      setMessages(response.data);
    } catch (e) {
      console.error("Failed to load chat history", e);
    }
  };

  const scrollToBottom = () => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = async (text) => {
    const query = text || input;
    if (!query.trim()) return;

    // Optimistically update user message
    const userMsg = { role: 'user', content: query, timestamp: new Date().toISOString() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      const response = await chatAPI.sendMessage(query, 'default', selectedLocation);
      const assistantMsg = { role: 'assistant', content: response.data.answer, timestamp: new Date().toISOString() };
      setMessages(prev => [...prev, assistantMsg]);
    } catch (e) {
      setError("Backend server unavailable.");
    } finally {
      setLoading(false);
    }
  };

  const handleClearHistory = async () => {
    if (!window.confirm("Clear chat history?")) return;
    try {
      await chatAPI.clearHistory();
      setMessages([]);
    } catch (e) {
      console.error("Failed to clear chat logs", e);
    }
  };

  return (
    <div className="flex-1 flex flex-col gap-6 overflow-hidden p-8 h-screen">
      {/* Header */}
      <div className="flex justify-between items-center flex-shrink-0">
        <div>
          <h2 className="text-3xl font-heading font-extrabold tracking-tight flex items-center gap-2">
            AI Climate Assistant
            <Sparkles className="w-6 h-6 text-emerald-400" />
          </h2>
          <p className="text-slate-400 text-sm mt-1">
            Query the local knowledge base about Urban Heat Island science, indices, and action plans.
          </p>
        </div>

        {messages.length > 0 && (
          <button
            onClick={handleClearHistory}
            className="flex items-center gap-1.5 px-3.5 py-2 border border-slate-800 hover:border-red-500/20 hover:bg-red-500/5 text-slate-400 hover:text-red-400 text-xs font-semibold rounded-xl transition-all"
          >
            <Trash2 className="w-4 h-4" />
            <span>Clear Logs</span>
          </button>
        )}
      </div>

      {/* Main Conversation Window */}
      <div className="flex-1 flex flex-col md:flex-row gap-6 min-h-0">
        {/* Chat History Panel */}
        <div className="flex-1 flex flex-col rounded-2xl glass-panel border border-slate-800/80 overflow-hidden min-h-0 bg-slate-950/20">
          <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-5">
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center gap-3 text-slate-500 p-8">
                <Bot className="w-12 h-12 text-slate-600 border border-slate-800 p-2.5 rounded-2xl bg-slate-900/30" />
                <div>
                  <p className="text-sm font-semibold text-slate-300">Welcome to Bengaluru Climate AI Assistant</p>
                  <p className="text-xs text-slate-500 mt-1 max-w-sm">
                    I can explain UHI causes, interpret NDVI index ratios, and outline targeted adaptation strategies for Bengaluru.
                  </p>
                </div>
              </div>
            ) : (
              messages.map((msg, i) => (
                <div 
                  key={i} 
                  className={`flex gap-3.5 max-w-[85%] ${msg.role === 'user' ? 'self-end flex-row-reverse' : 'self-start'}`}
                >
                  {/* Icon */}
                  <div className={`w-8 h-8 rounded-xl flex-shrink-0 flex items-center justify-center border shadow-md ${
                    msg.role === 'user' 
                      ? 'bg-slate-900 border-slate-800 text-slate-300' 
                      : 'bg-gradient-to-br from-emerald-500 to-cyan-500 border-emerald-400/20 text-slate-950 font-bold'
                  }`}>
                    {msg.role === 'user' ? <User className="w-4.5 h-4.5" /> : <Bot className="w-4.5 h-4.5" />}
                  </div>

                  {/* Bubble */}
                  <div className={`p-4 rounded-2xl leading-relaxed text-xs font-medium border ${
                    msg.role === 'user' 
                      ? 'bg-slate-900/80 border-slate-800/60 text-slate-100 rounded-tr-none' 
                      : 'bg-slate-900/40 border-slate-850 text-slate-200 rounded-tl-none'
                  }`}>
                    {/* Preserve markdown structure or carriage returns */}
                    <div className="whitespace-pre-line flex flex-col gap-1.5">
                      {msg.content}
                    </div>
                  </div>
                </div>
              ))
            )}

            {loading && (
              <div className="flex gap-3.5 self-start items-center">
                <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-emerald-500 to-cyan-500 flex items-center justify-center border border-emerald-400/20 text-slate-950 font-bold">
                  <Bot className="w-4.5 h-4.5" />
                </div>
                <div className="p-3.5 bg-slate-900/40 border border-slate-850 rounded-2xl rounded-tl-none flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            )}
            
            <div ref={chatBottomRef} />
          </div>

          {error && (
            <div className="p-3 bg-red-500/10 border-t border-red-500/20 text-red-400 text-xs flex items-center gap-2">
              <AlertCircle className="w-4.5 h-4.5 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Form */}
          <div className="p-4 border-t border-slate-800 bg-slate-900/10 flex gap-3">
            <input
              type="text"
              placeholder="Ask about NDVI, cooling costs, carbon targets..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              className="flex-1 bg-slate-950 border border-slate-850 rounded-xl py-3 px-4 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500/40"
            />
            <button
              onClick={() => handleSend()}
              disabled={loading || !input.trim()}
              className="p-3 bg-gradient-to-r from-emerald-500 to-cyan-500 text-slate-950 rounded-xl font-bold hover:shadow-lg hover:shadow-emerald-500/20 transition-all disabled:opacity-40 disabled:hover:shadow-none"
            >
              <Send className="w-4.5 h-4.5" />
            </button>
          </div>
        </div>

        {/* Suggestion Sidebar */}
        <div className="w-full md:w-72 p-5 rounded-2xl glass-panel border border-slate-800/80 flex flex-col gap-4 flex-shrink-0">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-300">
            <HelpCircle className="w-4.5 h-4.5 text-emerald-400" />
            <span>CLIMATE SCIENCE TOPICS</span>
          </div>
          
          <div className="flex flex-wrap md:flex-col gap-2 mt-1">
            {suggestedPrompts.map((prompt, i) => (
              <button
                key={i}
                onClick={() => handleSend(prompt)}
                className="text-left w-full p-3 bg-slate-900/40 border border-slate-850 rounded-xl text-xs font-semibold text-slate-400 hover:text-emerald-400 hover:border-emerald-500/20 hover:bg-slate-900/60 transition-all"
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIAssistant;
