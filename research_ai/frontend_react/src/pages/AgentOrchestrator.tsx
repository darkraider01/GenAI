import { useState, useEffect } from 'react';
import axios from 'axios';
import { Cpu, RefreshCw, Bot, History, Download } from 'lucide-react';
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
  const [step, setStep] = useState(0);

  const steps = [
    { name: 'Prior Art Discovery', agent: 'Lead Research Librarian', detail: 'Scanning global vector space for foundational papers...' },
    { name: 'Trend Velocity Analysis', agent: 'Scientometric Analyst', detail: 'Mapping technical trajectories and growth sectors...' },
    { name: 'Innovation Gap Mapping', agent: 'Architect of Innovation', detail: 'Identifying untapped white space and disconnects...' },
    { name: 'Methodology Architecture', agent: 'Principal Investigator', detail: 'Designing multi-stage experimental frameworks...' },
    { name: 'Strategic Proposal Synthesis', agent: 'Grant Strategist', detail: 'Crafting fundable narratives and technical justification...' },
    { name: 'Ultimate Report Curation', agent: 'Chief Research Officer', detail: 'Finalizing the Master Research Report & Novelty Validation...' }
  ];

  // Simple interval-based fake progress since backend doesn't stream steps yet
  // This helps "moderate speed" feel by keeping user informed
  useEffect(() => {
    let interval: any;
    if (loading) {
      setStep(0);
      interval = setInterval(() => {
        setStep(prev => (prev < 5 ? prev + 1 : prev));
      }, 15000); // 15s per step approx for "moderate" speed perception
    }
    return () => clearInterval(interval);
  }, [loading]);

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

  const handleDownload = async () => {
    if (!result || !topic) return;
    try {
      const res = await axios.post('http://localhost:8000/api/download-report', 
        { topic, markdown: result },
        { responseType: 'blob' }
      );
      
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      const safeTopic = topic.replace(/[^a-z0-9]/gi, '_').toLowerCase();
      link.setAttribute('download', `Master_Report_${safeTopic}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error("Download failed", err);
      alert("Error generating PDF report");
    }
  };

  return (
    <div style={{ height: '100%', display: 'flex', gap: '2rem' }}>
      
      {/* Left Sidebar for History */}
      <div className="glass-card" style={{ width: '320px', display: 'flex', flexDirection: 'column', padding: '1.5rem', overflowY: 'auto', borderRight: '1px solid rgba(139, 92, 246, 0.2)' }}>
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
          Launch the full specialized agent team to autonomously synthesize a comprehensive 
          PhD-level research report without human intervention.
        </p>

        {!loading && !result ? (
          <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', maxWidth: '800px', margin: '0 auto', textAlign: 'center', padding: '4rem 2rem' }}>
            
            <div style={{ marginBottom: '1rem' }}>
              <Cpu size={64} color="#8b5cf6" style={{ margin: '0 auto 1rem auto', opacity: 0.8 }} />
              <h2 style={{ fontSize: '1.5rem', color: 'white', borderBottom: 'none' }}>Initialize Research Synthesis</h2>
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
              disabled={!topic || loading} 
              style={{ padding: '1.25rem 2.5rem', fontSize: '1.1rem', background: 'linear-gradient(to right, #8b5cf6, #c084fc)', borderRadius: '12px' }}
            >
              🚀 Deploy Autonomous Hive Mind
            </button>
          </div>
        ) : loading ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', flex: 1 }}>
            <div style={{ display: 'flex', gap: '1.5rem', overflowX: 'auto', padding: '1rem', width: '100%', maxWidth: '900px', marginBottom: '3rem', justifyContent: 'center' }}>
              {steps.map((s, idx) => (
                <div key={idx} style={{ 
                  flex: 1, 
                  minWidth: '130px',
                  display: 'flex', 
                  flexDirection: 'column', 
                  alignItems: 'center', 
                  gap: '0.5rem',
                  opacity: idx === step ? 1 : 0.3,
                  transition: 'all 0.5s ease',
                  transform: idx === step ? 'scale(1.05)' : 'scale(0.95)'
                }}>
                  <div style={{ 
                    width: '40px', 
                    height: '40px', 
                    borderRadius: '50%', 
                    background: idx === step ? '#8b5cf6' : 'rgba(255,255,255,0.1)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                    fontWeight: 'bold',
                    boxShadow: idx === step ? '0 0 15px #8b5cf6' : 'none'
                  }}>
                    {idx + 1}
                  </div>
                  <div style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', color: idx === step ? '#c084fc' : 'white', textAlign: 'center' }}>{s.name}</div>
                </div>
              ))}
            </div>

            <div style={{ position: 'relative', width: '100px', height: '100px', marginBottom: '2rem' }}>
               <RefreshCw size={100} color="#8b5cf6" className="animate-spin" style={{ animationDuration: '3s' }} />
               <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)' }}>
                 <Bot size={32} color="white" />
               </div>
            </div>

            <div style={{ textAlign: 'center', background: 'rgba(139, 92, 246, 0.05)', padding: '2rem', borderRadius: '16px', border: '1px solid rgba(139, 92, 246, 0.2)', maxWidth: '500px' }}>
              <h2 style={{ color: 'white', fontSize: '1.4rem', borderBottom: 'none', marginBottom: '0.5rem' }}>{steps[step].agent}</h2>
              <p style={{ color: 'var(--accent)', fontWeight: 600, marginBottom: '1rem' }}>Active Phase: {steps[step].name}</p>
              <p style={{ color: 'var(--text-muted)', fontSize: '1rem' }}>
                {steps[step].detail}
              </p>
            </div>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', flex: 1 }}>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
              <button 
                className="btn" 
                onClick={handleDownload}
                style={{ background: 'rgba(139, 92, 246, 0.2)', border: '1px solid #8b5cf6', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
              >
                <Download size={18} />
                Download Master Report (PDF)
              </button>
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
