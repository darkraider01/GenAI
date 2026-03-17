import { useState } from 'react';
import axios from 'axios';
import { Microscope, Loader2, ExternalLink } from 'lucide-react';

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
      <p style={{ color: 'var(--text-muted)', marginBottom: '2rem', maxWidth: '800px', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        <span>
          Pumps input text against the high-dimensional vector space of all ingested literature. 
          Calculates geometric cosine distance to determine true structural novelty of the idea.
        </span>
        <span style={{ fontSize: '0.85rem', color: 'var(--accent)', background: 'rgba(6, 182, 212, 0.1)', padding: '0.75rem', borderRadius: '4px', border: '1px solid rgba(6, 182, 212, 0.2)' }}>
          <strong>How it works:</strong> We use the <code>BAAI/bge-large-en</code> transformer model to convert your proposal into a 1024-dimensional math vector. 
          This is then compared against thousands of existing research paper vectors using <strong>Cosine Similarity</strong>. 
          The novelty score is based on the inverse of the highest similarity found in our database.
        </span>
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
                    Max Similarity
                  </div>
               </div>

               <div>
                  <div style={{ fontSize: '3rem', fontWeight: 700, color: result.plagiarism_score > 50 ? '#f43f5e' : '#f59e0b', lineHeight: 1 }}>
                     {result.plagiarism_score.toFixed(0)}%
                  </div>
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.5rem', textTransform: 'uppercase', letterSpacing: '1px' }}>
                    Plagiarism Score
                  </div>
               </div>
            </div>
            
            {result.closest_paper && (
              <div style={{ background: 'rgba(15, 23, 42, 0.4)', padding: '1.5rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                  <h3 style={{ fontSize: '1rem', color: '#94a3b8', margin: 0 }}>Dangerously Close Existing Research:</h3>
                  {(result.closest_paper.pdf_url || result.closest_paper.url) && (
                    <a 
                      href={result.closest_paper.pdf_url || result.closest_paper.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="btn btn-secondary"
                      style={{ padding: '0.4rem 0.8rem', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem', textDecoration: 'none' }}
                    >
                      <ExternalLink size={14} /> Read Paper
                    </a>
                  )}
                </div>
                <div style={{ color: 'white', fontWeight: 500, marginBottom: '0.5rem' }}>{result.closest_paper.title}</div>
                <div style={{ fontSize: '0.85rem', color: 'var(--accent)', marginBottom: '1rem' }}>
                  Authors: {Array.isArray(result.closest_paper.authors) 
                    ? result.closest_paper.authors.join(', ') 
                    : (result.closest_paper.authors || 'Unknown')}
                </div>
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
