import { useState } from 'react';
import axios from 'axios';
import { Microscope, Loader2 } from 'lucide-react';

export default function NoveltyAnalyzer() {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleAnalyze = async () => {
    if (!text) return;
    setLoading(true);
    try {
      const res = await axios.post('http://localhost:8000/api/novelty-score', { proposal_text: text });
      setResult(res.data);
      if (!res.data || typeof res.data.novelty_score !== 'number') {
        alert('Unexpected response from server. Please try again.');
        setLoading(false);
        return;
      }
    } catch (err) {
      console.error(err);
      alert('Error analyzing novelty');
    }
    setLoading(false);
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return '#10b981'; // Green (Highly Novel)
    if (score >= 0.5) return '#f59e0b'; // Yellow (Moderately Novel)
    return '#ef4444'; // Red (Not Novel)
  };

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <h1 style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <Microscope color="#06b6d4" size={32} />
        Novelty Analyzer
      </h1>
      <p style={{ color: 'var(--text-muted)', marginBottom: '2rem', maxWidth: '800px' }}>
        Pumps input text against the high-dimensional vector space of all ingested literature. 
        Calculates geometric cosine distance to determine true structural novelty of the idea.
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: result ? '1fr 1fr' : '1fr', gap: '2rem' }}>
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div>
             <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>Abstract or Proposal Draft</label>
             <textarea 
               value={text}
               onChange={(e) => setText(e.target.value)}
               placeholder="Paste your research idea here..."
               className="input-field"
               style={{ minHeight: '300px', resize: 'vertical' }}
             />
          </div>
          
          <button 
            className="btn" 
            onClick={handleAnalyze}
            disabled={loading || !text}
            style={{ background: '#0891b2', alignSelf: 'flex-start' }}
          >
            {loading ? <Loader2 className="animate-spin" /> : 'Run Dimensional Analysis'}
          </button>
        </div>

        {result && (
          <div className="glass-card slide-in" style={{ borderColor: getScoreColor(result.novelty_score) }}>
            <h2 style={{ borderBottom: 'none', marginBottom: '2rem', color: 'white' }}>Analysis Results</h2>
            
            <div style={{ display: 'flex', justifyContent: 'space-around', marginBottom: '3rem', textAlign: 'center' }}>
               <div>
                  <div style={{ fontSize: '3rem', fontWeight: 700, color: getScoreColor(result.novelty_score), lineHeight: 1 }}>
                     {result.novelty_score.toFixed(2)}
                  </div>
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.5rem', textTransform: 'uppercase', letterSpacing: '1px' }}>
                    Novelty Score
                  </div>
               </div>
               
               <div>
                  <div style={{ fontSize: '3rem', fontWeight: 700, color: '#f43f5e', lineHeight: 1 }}>
                     {result.max_similarity.toFixed(2)}
                  </div>
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.5rem', textTransform: 'uppercase', letterSpacing: '1px' }}>
                    Max Similarity Found
                  </div>
               </div>
            </div>
            
            {result.closest_paper && (
              <div style={{ background: 'rgba(15, 23, 42, 0.4)', padding: '1.5rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                <h3 style={{ fontSize: '1rem', color: '#94a3b8', marginBottom: '1rem' }}>Dangerously Close Existing Research:</h3>
                <div style={{ color: 'white', fontWeight: 500, marginBottom: '0.5rem' }}>{result.closest_paper.title}</div>
                <div style={{ fontSize: '0.85rem', color: 'var(--accent)', marginBottom: '1rem' }}>Authors: {result.closest_paper.authors?.join(', ')}</div>
                <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                  {result.closest_paper.abstract}
                </p>
              </div>
            )}
            
            {!result.closest_paper && (
               <div style={{ textAlign: 'center', padding: '2rem', color: '#10b981' }}>
                 No highly similar papers found in the ingested literature. This concept appears structurally novel.
               </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
