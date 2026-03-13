import React, { useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { Search, Loader2 } from 'lucide-react';

export default function LiteratureReview() {
  const [topic, setTopic] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleGenerate = async () => {
    if (!topic) return;
    setLoading(true);
    try {
      const res = await axios.post('http://localhost:8000/api/literature-review', { topic });
      setResult(res.data);
    } catch (err) {
      console.error(err);
      alert('Error generating review');
    }
    setLoading(false);
  };

  return (
    <div>
      <h1 style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <Search color="#3b82f6" size={32} />
        Literature Review Generator
      </h1>
      <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>
        Enter a research topic. The Intelligence Engine will retrieve the top 30 papers, 
        cluster them into thematic horizons, and synthesize a formal survey.
      </p>

      <div className="glass-card" style={{ display: 'flex', gap: '1rem' }}>
        <input 
          type="text" 
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="e.g. Autonomous AI Agents for Code Generation..."
          className="input-field"
          style={{ marginBottom: 0 }}
          onKeyDown={(e) => e.key === 'Enter' && handleGenerate()}
        />
        <button 
          className="btn" 
          onClick={handleGenerate}
          disabled={loading || !topic}
          style={{ whiteSpace: 'nowrap' }}
        >
          {loading ? <Loader2 className="animate-spin" /> : 'Generate Review'}
        </button>
      </div>

      {result && (
        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 2fr) 1fr', gap: '2rem' }}>
          
          <div className="glass-card markdown-body" style={{ background: 'rgba(15, 23, 42, 0.9)' }}>
            <ReactMarkdown>{result.review}</ReactMarkdown>
          </div>
          
          <div>
            <div className="glass-card" style={{ padding: '1.5rem' }}>
              <h3 style={{ marginBottom: '1.5rem', color: 'white' }}>Discovered Themes</h3>
              {result.clusters?.map((c: any, i: number) => (
                <div key={i} style={{ marginBottom: '1rem', paddingBottom: '1rem', borderBottom: '1px solid var(--border-light)' }}>
                  <div style={{ fontWeight: 600, color: 'var(--accent)', marginBottom: '0.5rem' }}>
                    {c.theme_name} <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>({c.paper_count} papers)</span>
                  </div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                    {c.titles.slice(0, 3).map((t: string, j: number) => (
                      <div key={j} style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>• {t}</div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
            
            <div className="glass-card" style={{ padding: '1.5rem' }}>
               <h3 style={{ marginBottom: '1rem', color: 'white' }}>Context Sources ({result.papers_used?.length || 0})</h3>
               <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
                 {result.papers_used?.map((p: any, i: number) => (
                    <div key={i} style={{ fontSize: '0.8rem', marginBottom: '0.5rem' }}>
                      <span style={{ color: '#94a3b8' }}>[{p.year}]</span>
                      <strong style={{ marginLeft: '4px', color: '#cbd5e1' }}>{p.title}</strong>
                    </div>
                 ))}
               </div>
            </div>
          </div>
          
        </div>
      )}
    </div>
  );
}
