import { useState } from 'react';
import axios from 'axios';
import { PenTool, Download, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export default function ProposalGenerator() {
  const [topic, setTopic] = useState('');
  const [methodology, setMethodology] = useState('');
  const [loading, setLoading] = useState(false);
  const [markdown, setMarkdown] = useState('');

  const handleGenerate = async () => {
    if (!topic || !methodology) {
      alert("Please provide both a topic and a methodology plan.");
      return;
    }
    
    setLoading(true);
    try {
      const res = await axios.post('http://localhost:8000/api/generate-proposal', { 
        topic, 
        methodology 
      });
      setMarkdown(res.data.markdown);
    } catch (err) {
      console.error(err);
      alert('Error generating proposal');
    }
    setLoading(false);
  };

  const handleDownload = () => {
    // Basic text download. For real PDF we'd hit another endpoint, 
    // but demonstrating the raw blob here for speed
    const element = document.createElement("a");
    const file = new Blob([markdown], {type: 'text/markdown'});
    element.href = URL.createObjectURL(file);
    element.download = "IEEE_Grant_Proposal.md";
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <h1 style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <PenTool color="#ec4899" size={32} />
        Grant Proposal Generator
      </h1>
      <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>
        Synthesize an IEEE-compliant academic grant proposal pulling hard citations 
        from the database and applying formal objective linguistics.
      </p>

      {!markdown ? (
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', maxWidth: '800px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>Research Topic / Title</label>
            <input 
              type="text" 
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g. Federated Learning over Unreliable Networks..."
              className="input-field"
              style={{ marginBottom: 0 }}
            />
          </div>
          
          <div>
             <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>Target Methodology Plan (Paste from Method Planner)</label>
             <textarea 
               value={methodology}
               onChange={(e) => setMethodology(e.target.value)}
               placeholder="1. Dataset...\n2. Baselines...\n3. Architecture..."
               className="input-field"
               style={{ minHeight: '200px', resize: 'vertical' }}
             />
          </div>
          
          <button 
            className="btn" 
            onClick={handleGenerate}
            disabled={loading || !topic || !methodology}
            style={{ background: '#db2777', alignSelf: 'flex-start' }}
          >
            {loading ? <Loader2 className="animate-spin" /> : 'Synthesize Proposal'}
          </button>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', flex: 1 }}>
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
            <button className="btn" onClick={() => setMarkdown('')} style={{ background: 'transparent', border: '1px solid rgba(255,255,255,0.2)' }}>
              Edit Inputs
            </button>
            <button className="btn" onClick={handleDownload} style={{ background: '#ec4899' }}>
              <Download size={18} /> Export Markdown
            </button>
          </div>
          <div className="glass-card markdown-body" style={{ background: 'rgba(15, 23, 42, 0.9)', overflowY: 'auto' }}>
            <ReactMarkdown>{markdown}</ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  );
}
