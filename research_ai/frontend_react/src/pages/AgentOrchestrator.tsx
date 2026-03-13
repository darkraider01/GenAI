import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Cpu, RefreshCw, Bot, History } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface RunRecord {
  id: number;
  topic: string;
  result: string;
  timestamp: number;
}

export default function AgentOrchestrator() {
  const [topic, setTopic] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState('');
  const [history, setHistory] = useState<RunRecord[]>([]);

  const fetchHistory = async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/orchestrator_history');
      setHistory(res.data.history);
    } catch (err) {
      console.error("Could not fetch history", err);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleLaunch = async () => {
    if (!topic) return;
    setLoading(true);
    setResult(''); // clear old result
    try {
      const res = await axios.post('http://localhost:8000/api/orchestrator', { topic });
      setResult(res.data.result);
      fetchHistory();
    } catch (err) {
      console.error(err);
      alert('Error running swarm');
    }
    setLoading(false);
  };

  return (
    <div style={{ height: '100%', display: 'flex', gap: '2rem' }}>
      
      {/* Left Sidebar for History */}
      <div className="glass-card" style={{ width: '320px', display: 'flex', flexDirection: 'column', padding: '1.5rem', overflowY: 'auto' }}>
        <h2 style={{ fontSize: '1.2rem', color: 'white', display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '0.75rem' }}>
          <History size={20} color="#8b5cf6" />
          Swarm History
        </h2>
        
        {history.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', textAlign: 'center', marginTop: '2rem' }}>No previous runs yet.</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {history.map((run) => (
              <div 
                key={run.id}
                onClick={() => { setResult(run.result); setTopic(run.topic); }}
                style={{ 
                  padding: '1rem', 
                  background: 'rgba(255,255,255,0.03)', 
                  borderRadius: '12px', 
                  cursor: 'pointer',
                  border: '1px solid rgba(255,255,255,0.05)',
                  transition: 'all 0.2s ease'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.background = 'rgba(139, 92, 246, 0.1)';
                  e.currentTarget.style.borderColor = 'rgba(139, 92, 246, 0.3)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.background = 'rgba(255,255,255,0.03)';
                  e.currentTarget.style.borderColor = 'rgba(255,255,255,0.05)';
                }}
              >
                <div style={{ fontWeight: 500, color: 'white', marginBottom: '0.35rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {run.topic}
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  {new Date(run.timestamp * 1000).toLocaleString()}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Main Content Area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflowY: 'auto' }}>
        <h1 style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
          <Cpu color="#8b5cf6" size={32} />
          Autonomous Agent Swarm
        </h1>
        <p style={{ color: 'var(--text-muted)', marginBottom: '2rem', maxWidth: '800px' }}>
          Launch the full CrewAI agent team (Researcher, Trend Analyst, Gap Detector, Method Designer, Proposal Writer, and Scorer) 
          to autonomously synthesize an end-to-end proposal entirely without human intervention.
        </p>

        {!loading && !result ? (
          <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', maxWidth: '800px', margin: '0 auto', textAlign: 'center', padding: '4rem 2rem' }}>
            
            <div style={{ marginBottom: '1rem' }}>
              <Cpu size={64} color="#8b5cf6" style={{ margin: '0 auto 1rem auto', opacity: 0.8 }} />
              <h2 style={{ fontSize: '1.5rem', color: 'white', borderBottom: 'none' }}>Initialize Core Architecture</h2>
            </div>

            <div style={{ textAlign: 'left' }}>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>Target Research Domain</label>
              <input 
                type="text" 
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g. Agentic Frameworks for Scientific Discovery..."
                className="input-field"
                style={{ padding: '1.25rem', fontSize: '1.1rem' }}
                onKeyDown={(e) => e.key === 'Enter' && handleLaunch()}
              />
            </div>
            
            <button 
              className="btn" 
              onClick={handleLaunch}
              disabled={!topic || history.some(h => h.topic === topic && !loading)} 
              // Avoid exact duplicate spam if they just clicked it, but let them if they want
              style={{ padding: '1rem 2rem', fontSize: '1.1rem', background: 'linear-gradient(to right, #8b5cf6, #c084fc)' }}
            >
              Deploy AI Agent Swarm
            </button>
          </div>
        ) : loading ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', flex: 1 }}>
            <div style={{ position: 'relative', width: '120px', height: '120px', marginBottom: '2rem' }}>
               <RefreshCw size={120} color="#8b5cf6" className="animate-spin" style={{ animationDuration: '3s' }} />
               <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)' }}>
                 <Bot size={40} color="white" />
               </div>
            </div>
            <h2 style={{ color: 'white', fontSize: '1.5rem', borderBottom: 'none' }}>Agents Collaborating...</h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '1.1rem', maxWidth: '400px', textAlign: 'center' }}>
              The hive mind is actively reasoning, designing methodologies, and synthesizing text. This may take several minutes.
            </p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', flex: 1 }}>
            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <button 
                className="btn" 
                onClick={() => { setResult(''); setTopic(''); }} 
                style={{ background: 'transparent', border: '1px solid rgba(255,255,255,0.2)' }}
              >
                New Swarm Mission
              </button>
            </div>
            <div className="glass-card markdown-body" style={{ background: 'rgba(15, 23, 42, 0.9)', overflowY: 'auto', flex: 1 }}>
              <ReactMarkdown>{result}</ReactMarkdown>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
