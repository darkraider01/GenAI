import { useState } from 'react';
import axios from 'axios';
import { Compass, RefreshCw, Zap, Lightbulb, Target, TrendingUp, CheckCircle2, BarChart3, Info, ExternalLink } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { useNavigate } from 'react-router-dom';

export default function GapFinder() {
  const [gaps, setGaps] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [savedIds, setSavedIds] = useState<Set<number>>(new Set());
  const [animatingId, setAnimatingId] = useState<number | null>(null);
  const [targetId, setTargetId] = useState<number | null>(null);
  const navigate = useNavigate();

  const fetchGaps = async () => {
    setGaps([]);
    setLoading(true);
    try {
      const res = await axios.get('http://localhost:8000/api/gaps');
      setGaps(res.data);
    } catch (err) {
      console.error(err);
      alert('Failed to detect research niches');
    }
    setLoading(false);
  };

  const handleSave = (id: number) => {
    setAnimatingId(id);
    setSavedIds(prev => new Set(prev).add(id));
    setTimeout(() => setAnimatingId(null), 1000);
  };

  const handleExplore = (id: number, keywords: string) => {
    setTargetId(id);
    // Add a small delay for the animation to be seen before navigating
    setTimeout(() => {
      navigate(`/app/explorer?q=${encodeURIComponent(keywords)}`);
      setTargetId(null);
    }, 600);
  };

  return (
    <div className="gap-finder-container" style={{ maxWidth: '1100px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '3rem', padding: '1.5rem', background: 'rgba(245, 158, 11, 0.05)', borderRadius: '16px', border: '1px solid rgba(245, 158, 11, 0.2)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          <div style={{ background: '#f59e0b', padding: '1rem', borderRadius: '12px', boxShadow: '0 0 25px rgba(245, 158, 11, 0.4)' }}>
            <Compass color="black" size={32} />
          </div>
          <div>
            <h1 style={{ fontSize: '2.2rem', margin: 0, color: 'white', letterSpacing: '-0.5px' }}>Niche & Gap Discovery</h1>
            <p style={{ color: 'var(--text-muted)', marginTop: '0.25rem', fontSize: '1rem' }}>
              Identifying the next 'Hot Topics' by analyzing semantic overlaps in trending fields.
            </p>
          </div>
        </div>
        <button 
          className="btn" 
          onClick={fetchGaps} 
          disabled={loading} 
          style={{ 
            background: 'linear-gradient(135deg, #f59e0b, #d97706)', 
            color: 'white',
            padding: '1.25rem 2.5rem',
            fontSize: '1.1rem',
            border: 'none',
            borderRadius: '12px',
            boxShadow: '0 10px 25px -5px rgba(245, 158, 11, 0.5)',
            transform: loading ? 'scale(0.98)' : 'scale(1)',
            transition: 'all 0.3s ease'
          }}
        >
          {loading ? <><RefreshCw className="animate-spin" /> Analyzing Corpus...</> : <><Zap size={18} /> Discover Research Niches</>}
        </button>
      </div>

      {loading && (
        <div style={{ textAlign: 'center', margin: '6rem 0' }}>
            <div className="loader" style={{ width: '50px', height: '50px', borderTopColor: '#f59e0b', borderLeftColor: 'transparent' }}></div>
            <p style={{ marginTop: '2rem', color: '#f59e0b', fontSize: '1.3rem', fontWeight: 500, letterSpacing: '0.5px' }}>
              Heuristic engines are sweeping the literature for unseen crossovers...
            </p>
        </div>
      )}

      {gaps.length > 0 && !loading && (
        <div style={{ animation: 'fadeIn 0.6s ease' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '2.5rem', color: '#fcd34d' }}>
            <TrendingUp size={24} />
            <span style={{ fontWeight: 700, letterSpacing: '1px', fontSize: '0.9rem' }}>TOP HIGH-MOMENTUM NICHES DISCOVERED</span>
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '2.5rem' }}>
            {gaps.map((g, i) => (
              <div key={i} className="glass-card niche-card" style={{ 
                padding: '3.5rem', 
                borderLeft: '6px solid #f59e0b',
                background: 'rgba(15, 23, 42, 0.98)',
                position: 'relative',
                overflow: 'hidden',
                borderRadius: '24px'
              }}>
                <div style={{ position: 'absolute', top: '2rem', right: '2rem' }}>
                  <div style={{ background: 'rgba(245, 158, 11, 0.1)', color: '#f59e0b', padding: '0.6rem 1.25rem', borderRadius: '10px', fontSize: '0.85rem', fontWeight: 800, border: '1px solid rgba(245, 158, 11, 0.3)' }}>
                    MOMENTUM SCORE: {g.gap_score?.toFixed(2) || 'N/A'}
                  </div>
                </div>

                <div className="markdown-body" style={{ fontSize: '1.15rem' }}>
                  <ReactMarkdown>{g.gap_description}</ReactMarkdown>
                </div>

                {/* Quantitative Evidence & Explainability */}
                <div style={{ marginTop: '2.5rem', background: 'rgba(255,255,255,0.02)', padding: '2rem', borderRadius: '16px', border: '1px solid rgba(255,255,255,0.05)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1.5rem', color: '#94a3b8' }}>
                    <BarChart3 size={18} />
                    <span style={{ fontSize: '0.85rem', fontWeight: 700, letterSpacing: '1px' }}>DATA-DRIVEN EVIDENCE</span>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem', marginBottom: '2rem' }}>
                    <div style={{ padding: '1rem', background: 'rgba(15, 23, 42, 0.4)', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.03)' }}>
                      <div style={{ fontSize: '0.75rem', color: '#64748b', marginBottom: '0.25rem' }}>Mathematical Similarity</div>
                      <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'white' }}>{(g.similarity * 100).toFixed(1)}%</div>
                    </div>
                    <div style={{ padding: '1rem', background: 'rgba(15, 23, 42, 0.4)', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.03)' }}>
                      <div style={{ fontSize: '0.75rem', color: '#64748b', marginBottom: '0.25rem' }}>Cluster 1 Density</div>
                      <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'white' }}>{g.t1_density} Papers</div>
                    </div>
                    <div style={{ padding: '1rem', background: 'rgba(15, 23, 42, 0.4)', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.03)' }}>
                      <div style={{ fontSize: '0.75rem', color: '#64748b', marginBottom: '0.25rem' }}>Cluster 2 Density</div>
                      <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'white' }}>{g.t2_density} Papers</div>
                    </div>
                  </div>

                  {g.supporting_papers && g.supporting_papers.length > 0 && (
                    <div>
                      <div style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <Info size={14} /> Supporting Evidence from Corpus:
                      </div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                        {g.supporting_papers.map((paper: any, pIdx: number) => (
                          <a 
                            key={pIdx}
                            href={paper.pdf_url || '#'}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{ 
                              display: 'flex', 
                              justifyContent: 'space-between', 
                              alignItems: 'center',
                              padding: '1rem 1.25rem', 
                              background: 'rgba(255,255,255,0.03)', 
                              borderRadius: '8px', 
                              textDecoration: 'none',
                              border: '1px solid transparent',
                              transition: 'all 0.2s ease'
                            }}
                            className="supporting-paper-link"
                          >
                            <div style={{ flex: 1 }}>
                              <div style={{ color: 'white', fontSize: '0.9rem', fontWeight: 500, marginBottom: '0.15rem' }}>{paper.title}</div>
                              <div style={{ color: '#64748b', fontSize: '0.75rem' }}>{paper.authors}</div>
                            </div>
                            <ExternalLink size={16} style={{ color: '#f59e0b', marginLeft: '1rem' }} />
                          </a>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                <div style={{ marginTop: '3rem', display: 'flex', gap: '1.5rem' }}>
                  <button 
                    className={`btn ${animatingId === i ? 'animate-glow' : ''}`} 
                    onClick={() => handleSave(i)}
                    style={{ 
                      background: savedIds.has(i) ? 'rgba(34, 197, 94, 0.15)' : 'rgba(255,255,255,0.03)', 
                      border: '1px solid rgba(255,255,255,0.1)', 
                      fontSize: '0.95rem',
                      padding: '1rem 2rem',
                      borderRadius: '10px',
                      color: savedIds.has(i) ? '#4ade80' : 'white',
                      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
                    }}
                  >
                    {savedIds.has(i) ? <CheckCircle2 size={18} /> : <Lightbulb size={18} style={{ transition: 'color 0.3s' }} />}
                    {savedIds.has(i) ? 'Saved to Project' : 'Save for My Project'}
                  </button>
                  <button 
                    className={`btn ${targetId === i ? 'animate-target' : ''}`} 
                    onClick={() => handleExplore(i, `${g.t1_keywords} ${g.t2_keywords}`)}
                    style={{ 
                      background: 'rgba(139, 92, 246, 0.05)', 
                      border: '1px solid rgba(139, 92, 246, 0.2)', 
                      fontSize: '0.95rem',
                      padding: '1rem 2rem',
                      borderRadius: '10px',
                      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
                    }}
                  >
                    <Target size={18} /> Explore This Context
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {!loading && gaps.length === 0 && (
         <div style={{ textAlign: 'center', padding: '8rem 2rem', border: '2px dashed rgba(255,255,255,0.05)', borderRadius: '32px', background: 'rgba(255,255,255,0.01)' }}>
            <div style={{ background: 'rgba(245, 158, 11, 0.1)', width: '100px', height: '100px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 2rem auto' }}>
              <Lightbulb size={48} style={{ color: '#f59e0b', opacity: 0.6 }} />
            </div>
            <h2 style={{ color: 'white', fontSize: '1.8rem', borderBottom: 'none' }}>Ready to find your next research topic?</h2>
            <p style={{ color: 'var(--text-muted)', maxWidth: '600px', margin: '1rem auto', fontSize: '1.1rem' }}>
              Our heuristic engine sweeps thousands of paper semantic vectors to find unexplored crossovers between high-growth domains.
            </p>
         </div>
      )}
    </div>
  );
}
