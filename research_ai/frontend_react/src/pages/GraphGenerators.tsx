import React, { useState } from 'react';
import { BarChart3, Lightbulb, Zap, Download, RefreshCcw } from 'lucide-react';

const API = 'http://localhost:8000';

export default function GraphGenerators() {
  const [topic, setTopic] = useState('');
  const [customData, setCustomData] = useState('');
  const [fileName, setFileName] = useState('');
  const [loadingIdeas, setLoadingIdeas] = useState(false);
  const [ideas, setIdeas] = useState<any[]>([]);
  const [generatingGraph, setGeneratingGraph] = useState<string | null>(null);
  const [generatedImage, setGeneratedImage] = useState<string | null>(null);


  const getIdeas = async () => {
    if (!topic.trim()) return;
    setLoadingIdeas(true);
    setGeneratedImage(null);
    try {
      const res = await fetch(`${API}/api/graph-ideas`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic, custom_data: customData }),
      });
      const data = await res.json();
      setIdeas(data.ideas || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingIdeas(false);
    }
  };

  const generateGraph = async (idea: any) => {
    setGeneratingGraph(idea.title);
    try {
      const res = await fetch(`${API}/api/generate-graph`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idea, topic }),
      });
      const data = await res.json();
      setGeneratedImage(`${API}${data.image_url}`);
    } catch (e) {
      console.error(e);
    } finally {
      setGeneratingGraph(null);
    }
  };

  const generateDirectGraph = async () => {
    if (!customData) return;
    setGeneratingGraph("Direct Plot");
    try {
      const res = await fetch(`${API}/api/plot-csv`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic, custom_data: customData }),
      });
      const data = await res.json();
      setGeneratedImage(`${API}${data.image_url}`);
    } catch (e) {
      console.error(e);
    } finally {
      setGeneratingGraph(null);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setFileName(file.name);
      const reader = new FileReader();
      reader.onload = (event) => {
        if (event.target?.result) {
          setCustomData(event.target.result as string);
        }
      };
      reader.readAsText(file);
    }
  };

  return (
    <div className="animate-fade-in">
      <div className="mb-8">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
          Graph Intelligence Agent
        </h1>
        <p className="text-slate-400 mt-2">
          Generate high-impact visualization ideas and production-ready graphs for your research paper.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1 space-y-6">
          <div className="glass-card p-6">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500 mb-4">Research Topic</h3>
            <div className="flex flex-col gap-4">
              <input 
                className="input-field"
                placeholder="e.g. Impact of Transformer models on NLP"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
              />
              <div className="flex flex-col gap-2">
                <label className="text-xs font-semibold text-slate-400">Optional: Upload Custom Data (CSV/TXT)</label>
                <div className="relative">
                  <input 
                    type="file" 
                    accept=".csv,.txt"
                    onChange={handleFileUpload}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  />
                  <div className="flex items-center justify-between px-4 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-sm text-slate-300 pointer-events-none">
                    <span className="truncate">{fileName || "Choose file..."}</span>
                    <Download size={16} className="text-slate-500" />
                  </div>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3 mt-4">
                <button 
                  className="btn btn-primary text-xs py-3 flex items-center justify-center gap-2" 
                  onClick={getIdeas}
                  disabled={loadingIdeas}
                >
                  {loadingIdeas ? <RefreshCcw className="animate-spin size-4" /> : <Lightbulb size={16} />}
                  Get Ideas
                </button>
                <button 
                  className="btn btn-secondary text-xs py-3 flex items-center justify-center gap-2" 
                  onClick={generateDirectGraph}
                  disabled={!customData || generatingGraph === "Direct Plot"}
                >
                  {generatingGraph === "Direct Plot" ? <RefreshCcw className="animate-spin size-4" /> : <BarChart3 size={16} />}
                  Plot CSV
                </button>
              </div>
            </div>
          </div>

          {ideas.length > 0 && (
            <div className="glass-card p-6 space-y-4">
              <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500">Visualization Ideas</h3>
              {ideas.map((idea, i) => (
                <div key={i} className="p-4 bg-slate-800/50 rounded-xl border border-slate-700/50 hover:border-blue-500/50 transition-colors">
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="font-semibold text-blue-300">{idea.title}</h4>
                    <span className="text-[10px] px-2 py-0.5 bg-blue-500/20 text-blue-400 rounded-full border border-blue-500/30 uppercase font-bold">
                      {idea.type}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mb-4">{idea.description}</p>
                  <button 
                    className="btn btn-secondary w-full text-xs py-2"
                    onClick={() => generateGraph(idea)}
                    disabled={generatingGraph === idea.title}
                  >
                    {generatingGraph === idea.title ? <RefreshCcw className="animate-spin size-3" /> : <Zap size={14} />}
                    Generate This Graph
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="lg:col-span-2">
          <div className="glass-card min-h-[500px] flex flex-col items-center justify-center p-8 text-center">
            {!generatedImage && !generatingGraph ? (
              <div className="space-y-4">
                <div className="size-20 bg-slate-800/50 rounded-full flex items-center justify-center mx-auto border border-slate-700">
                  <BarChart3 size={40} className="text-slate-600" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-slate-300">Preview Canvas</h3>
                  <p className="text-slate-500 max-w-sm mx-auto">
                    Select a graph idea from the sidebar to generate a preview of your visualization.
                  </p>
                </div>
              </div>
            ) : generatingGraph ? (
              <div className="space-y-6">
                <div className="relative">
                  <div className="size-32 border-4 border-blue-500/20 border-t-blue-500 rounded-full animate-spin"></div>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <BarChart3 className="text-blue-500 animate-pulse" size={32} />
                  </div>
                </div>
                <p className="text-lg font-medium text-slate-300">Synthesizing Data & Generating Plot...</p>
              </div>
            ) : (
              <div className="w-full space-y-6">
                <div className="flex justify-between items-center w-full mb-4">
                  <h3 className="text-xl font-bold text-blue-400">Generated Visualization</h3>
                  <a 
                    href={generatedImage!} 
                    download="research_graph.png"
                    className="btn btn-secondary py-2 px-4 text-xs"
                  >
                    <Download size={14} /> Download Asset
                  </a>
                </div>
                <div className="bg-slate-900/80 rounded-2xl p-4 border border-slate-700/30 shadow-2xl">
                  <img 
                    src={generatedImage!} 
                    alt="Generated Graph" 
                    className="w-full rounded-lg shadow-inner"
                  />
                </div>
                <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-xl text-left">
                  <p className="text-xs text-blue-300 leading-relaxed italic">
                    Note: This is a high-fidelity mock graph based on the research context. Use the "Download Asset" button to include it in your final presentation.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
