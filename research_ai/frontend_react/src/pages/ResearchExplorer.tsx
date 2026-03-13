import React, { useState } from 'react';
import axios from 'axios';
import { Telescope, Loader2, Bot } from 'lucide-react';

export default function ResearchExplorer() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any[]>([]);

  const handleSearch = async () => {
    if (!query) return;
    setLoading(true);
    try {
      const res = await axios.post('http://localhost:8000/api/search', { query });
      setResults(res.data);
    } catch (err) {
      console.error(err);
      alert('Error searching corpus');
    }
    setLoading(false);
  };

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <h1 style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <Telescope color="#6366f1" size={32} />
        Research Explorer
      </h1>
      <p style={{ color: 'var(--text-muted)', marginBottom: '2rem', maxWidth: '800px' }}>
        A semantic vector search querying directly against the pre-computed HDBSCAN embeddings. 
        Ask natural language questions to find the most conceptually relevant academic papers in the corpus.
      </p>

      <div className="glass-card" style={{ display: 'flex', gap: '1rem' }}>
        <input 
          type="text" 
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g. How are diffusion networks being used for segmentation?"
          className="input-field"
          style={{ marginBottom: 0 }}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
        />
        <button 
          className="btn" 
          onClick={handleSearch}
          disabled={loading || !query}
          style={{ whiteSpace: 'nowrap', background: '#4f46e5' }}
        >
          {loading ? <Loader2 className="animate-spin" /> : 'Semantic Search'}
        </button>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', flex: 1, overflowY: 'auto' }}>
        {results.map((r, i) => (
          <div key={i} className="glass-card" style={{ position: 'relative', overflow: 'hidden' }}>
            <div style={{ position: 'absolute', top: 0, left: 0, width: '4px', height: '100%', background: '#6366f1' }} />
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
              <h3 style={{ fontSize: '1.25rem', color: 'white', margin: 0, lineHeight: 1.3 }}>{r.title}</h3>
              <div style={{ background: 'rgba(99, 102, 241, 0.1)', color: '#818cf8', padding: '0.25rem 0.75rem', borderRadius: '12px', fontSize: '0.85rem', whiteSpace: 'nowrap', marginLeft: '1rem' }}>
                Score: {(r.similarity || 0).toFixed(3)}
              </div>
            </div>
            
            <div style={{ color: 'var(--accent)', fontSize: '0.9rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
               <span>{r.year}</span>
               <span style={{ color: 'rgba(255,255,255,0.2)' }}>•</span>
               <span style={{ color: '#94a3b8' }}>{Array.isArray(r.authors) ? r.authors.join(', ') : r.authors}</span>
            </div>
            
            <p style={{ color: '#cbd5e1', lineHeight: 1.6, fontSize: '0.95rem' }}>
              {r.abstract}
            </p>
          </div>
        ))}
        {results.length === 0 && !loading && query && (
           <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
             <Bot size={48} opacity={0.5} style={{ display: 'block', margin: '0 auto 1rem' }} />
             No semantic matches found. The index might be empty.
           </div>
        )}
      </div>
    </div>
  );
}
