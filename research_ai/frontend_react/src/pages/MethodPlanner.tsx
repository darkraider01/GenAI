import { useState } from 'react';
import axios from 'axios';
import { PencilRuler, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export default function MethodPlanner() {
  const [topic, setTopic] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleGenerate = async () => {
    if (!topic) return;
    setLoading(true);
    try {
      const res = await axios.post('http://localhost:8000/api/method-plan', { topic });
      setResult(res.data);
    } catch (err) {
      console.error(err);
      alert('Error generating plan');
    }
    setLoading(false);
  };

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <h1 style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <PencilRuler color="#f43f5e" size={32} />
        Methodology Planner
      </h1>
      <p style={{ color: 'var(--text-muted)', marginBottom: '2rem', maxWidth: '800px' }}>
        Input a high-impact research gap. The Scientific AI will structurally design an experimental approach 
        including Dataset Selection, Baseline Architectures, Evaluation Metrics, and Computational constraints.
      </p>

      <div className="glass-card" style={{ display: 'flex', gap: '1rem' }}>
        <input 
          type="text" 
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="e.g. Applying Flow Matching to Federated Graph Learning..."
          className="input-field"
          style={{ marginBottom: 0 }}
          onKeyDown={(e) => e.key === 'Enter' && handleGenerate()}
        />
        <button 
          className="btn" 
          onClick={handleGenerate}
          disabled={loading || !topic}
          style={{ whiteSpace: 'nowrap', background: '#e11d48' }}
        >
          {loading ? <Loader2 className="animate-spin" /> : 'Design Experiment'}
        </button>
      </div>

      {result && (
        <div className="glass-card markdown-body" style={{ background: 'rgba(15, 23, 42, 0.9)', flex: 1, overflowY: 'auto' }}>
          <ReactMarkdown>{result.plan_markdown}</ReactMarkdown>
        </div>
      )}
    </div>
  );
}
