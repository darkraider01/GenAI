import { useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { Search, Loader2, Copy, CheckCircle2 } from 'lucide-react';

export default function LiteratureReview() {
  const [topic, setTopic] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [copied, setCopied] = useState(false);

  const handleGenerate = async () => {
    if (!topic) return;
    setLoading(true);
    try {
      const res = await axios.post(`http://${window.location.hostname}:8000/api/literature-review`, { topic });
      setResult(res.data);
    } catch (err) {
      console.error(err);
      alert('Error generating review');
    }
    setLoading(false);
  };

  const handleCopy = () => {
    if (result?.review) {
      navigator.clipboard.writeText(result.review);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="lit-review-container" style={{ maxWidth: '900px', margin: '0 auto' }}>
      <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <h1 style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
          <Search color="#3b82f6" size={36} />
          Literature Review Generator
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '1.1rem' }}>
          Synthesize high-quality academic surveys from recent literature.
        </p>
      </div>

      <div className="glass-card" style={{ display: 'flex', gap: '1rem', padding: '1rem' }}>
        <input 
          type="text" 
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="e.g. Autonomous AI Agents for Code Generation..."
          className="input-field"
          style={{ marginBottom: 0, flex: 1 }}
          onKeyDown={(e) => e.key === 'Enter' && handleGenerate()}
        />
        <button 
          className="btn" 
          onClick={handleGenerate}
          disabled={loading || !topic}
          style={{ minWidth: '160px' }}
        >
          {loading ? <Loader2 className="animate-spin" /> : 'Generate Review'}
        </button>
      </div>

      {result && (
        <div style={{ animation: 'fadeIn 0.5s ease' }}>
          
          <div className="glass-card markdown-body" style={{ 
            background: 'rgba(15, 23, 42, 0.95)', 
            padding: '4rem',
            position: 'relative',
            boxShadow: '0 20px 50px rgba(0,0,0,0.5)',
            border: '1px solid rgba(255,255,255,0.05)'
          }}>
            <button 
              onClick={handleCopy}
              className="btn"
              style={{
                position: 'absolute',
                top: '2rem',
                right: '2rem',
                background: copied ? 'var(--success)' : 'rgba(255,255,255,0.05)',
                padding: '0.5rem 1rem',
                fontSize: '0.8rem',
                border: '1px solid var(--border-light)'
              }}
            >
              {copied ? <><CheckCircle2 size={16} /> Copied!</> : <><Copy size={16} /> Copy Review</>}
            </button>
            <ReactMarkdown>{result.review}</ReactMarkdown>
          </div>
          
          <div className="glass-card" style={{ padding: '2rem', marginTop: '2rem' }}>
             <h3 style={{ marginBottom: '1.5rem', color: 'white', borderBottom: '1px solid var(--border-light)', paddingBottom: '0.5rem' }}>
               References & Context Sources
             </h3>
             <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))', gap: '1rem' }}>
               {result.papers_used?.map((p: any, i: number) => (
                  <div key={i} style={{ fontSize: '0.85rem', color: 'var(--text-muted)', display: 'flex', gap: '10px' }}>
                    <span style={{ color: 'var(--accent)', fontWeight: 600 }}>[{p.year}]</span>
                    <span style={{ color: '#cbd5e1' }}>{p.title}</span>
                  </div>
               ))}
             </div>
          </div>
          
        </div>
      )}
    </div>
  );
}
