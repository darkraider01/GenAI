import React, { useState } from 'react';
import axios from 'axios';
import { Compass, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export default function GapFinder() {
  const [gaps, setGaps] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchGaps = async () => {
    setLoading(true);
    try {
      const res = await axios.get('http://localhost:8000/api/gaps');
      setGaps(res.data);
    } catch (err) {
      console.error(err);
      alert('Failed to detect gaps');
    }
    setLoading(false);
  };

  // Group by type
  const groupedGaps: Record<string, any[]> = {};
  gaps.forEach(g => {
    const type = g.gap_type || 'Cross-Domain Gap';
    if (!groupedGaps[type]) groupedGaps[type] = [];
    groupedGaps[type].push(g);
  });

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem' }}>
        <div>
          <h1 style={{ display: 'flex', alignItems: 'center', gap: '1rem', margin: 0 }}>
            <Compass color="#f59e0b" size={32} />
            Research Gap Finder
          </h1>
          <p style={{ color: 'var(--text-muted)', marginTop: '0.5rem' }}>
            Automatically detect missing methodological or domain crossovers with high momentum scores.
          </p>
        </div>
        <button className="btn" onClick={fetchGaps} disabled={loading} style={{ background: '#f59e0b', color: 'black' }}>
          {loading ? <Loader2 className="animate-spin" /> : 'Run Heuristic Sweep'}
        </button>
      </div>

      {gaps.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '3rem' }}>
          {Object.entries(groupedGaps).map(([type, items], idx) => (
            <div key={idx}>
              <h2 style={{ fontSize: '1.5rem', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '0.5rem', marginBottom: '1.5rem' }}>
                {type}s
              </h2>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))', gap: '1.5rem' }}>
                {items.map((g, i) => (
                  <div key={i} className="glass-card" style={{ marginBottom: 0, borderTop: '4px solid #f59e0b' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem', alignItems: 'center' }}>
                      <span className="badge" style={{ background: 'rgba(245, 158, 11, 0.15)', color: '#fcd34d', borderColor: 'rgba(245, 158, 11, 0.3)', margin: 0 }}>
                        Score: {g.gap_score?.toFixed(2) || 'N/A'}
                      </span>
                    </div>
                    <div className="markdown-body" style={{ fontSize: '0.95rem' }}>
                      {g.gap_description ? (
                        <ReactMarkdown>{g.gap_description}</ReactMarkdown>
                      ) : (
                         <em>Raw gap extracted. Run LLM enhancer for readability.</em>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
