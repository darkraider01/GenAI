import React, { useState } from 'react';
import axios from 'axios';
import { UploadCloud, FileText, ChevronDown, ChevronRight, CheckCircle2, AlertTriangle, Lightbulb } from 'lucide-react';

const Collapsible = ({ title, children, defaultOpen = true, icon: Icon }: any) => {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="collapsible">
      <div className="collapsible-header" onClick={() => setOpen(!open)}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          {Icon && <Icon size={18} color="var(--accent)" />}
          {title}
        </div>
        {open ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
      </div>
      {open && <div className="collapsible-content">{children}</div>}
    </div>
  );
};

export default function PaperReader() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const res = await axios.post('http://localhost:8000/api/analyze-paper', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      setResult(res.data);
    } catch (err) {
      console.error(err);
      alert('Error parsing PDF');
    }
    setLoading(false);
  };

  return (
    <div>
      <h1 style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <FileText color="#10b981" size={32} />
        Paper Reading Assistant
      </h1>
      <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>
        Upload any academic PDF. The engine will rapidly consume the text,
        identify structural components, and extract core scientific metadata automatically.
      </p>

      <div className="glass-card" style={{ 
        display: 'flex', 
        flexDirection: 'column', 
        alignItems: 'center', 
        justifyContent: 'center',
        padding: '3rem',
        borderStyle: 'dashed',
        borderColor: file ? 'var(--success)' : 'rgba(255,255,255,0.2)',
        cursor: 'pointer'
      }}>
        <input 
          type="file" 
          accept="application/pdf"
          id="pdf-upload"
          style={{ display: 'none' }}
          onChange={(e) => {
            if (e.target.files && e.target.files.length > 0) {
              setFile(e.target.files[0]);
            }
          }}
        />
        <label htmlFor="pdf-upload" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', cursor: 'pointer', gap: '1rem' }}>
          <UploadCloud size={48} color={file ? '#10b981' : '#94a3b8'} />
          <div style={{ fontSize: '1.25rem', fontWeight: 500 }}>
            {file ? file.name : 'Click or drag PDF to upload'}
          </div>
          <div style={{ color: 'var(--text-muted)' }}>Maximum size: 20MB</div>
        </label>
        
        {file && (
          <button 
            className="btn" 
            style={{ marginTop: '2rem', padding: '1rem 3rem', background: 'var(--success)' }}
            onClick={(e) => { e.stopPropagation(); handleUpload(); }}
            disabled={loading}
          >
            {loading ? <div className="loader"></div> : 'Extract & Analyze Paper'}
          </button>
        )}
      </div>

      {result && (
        <div style={{ marginTop: '3rem' }}>
          <h2 style={{ background: 'linear-gradient(to right, #fff, #94a3b8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', borderBottom: 'none' }}>
            {result.title}
          </h2>
          <div style={{ color: 'var(--accent)', marginBottom: '2rem', fontWeight: 500 }}>
            {result.year} • {result.authors?.join(', ')}
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
            <Collapsible title="Key Contributions" defaultOpen={true} icon={CheckCircle2}>
               <ul style={{ paddingLeft: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                 {result.contributions?.map((c: string, i: number) => <li key={i}>{c}</li>)}
               </ul>
            </Collapsible>
            
            <Collapsible title="Methodology Overview" defaultOpen={true}>
              <div style={{ lineHeight: 1.7 }}>{result.methodology}</div>
            </Collapsible>
            
            <Collapsible title="Datasets & Evaluation" defaultOpen={true}>
              <div style={{ marginBottom: '1rem' }}>
                <strong style={{ color: 'white', display: 'block', marginBottom: '0.5rem' }}>Datasets Used:</strong>
                {result.datasets?.map((d: string, i: number) => <span key={i} className="badge">{d}</span>)}
              </div>
              <div>
                <strong style={{ color: 'white', display: 'block', marginBottom: '0.5rem' }}>Metrics:</strong>
                {result.evaluation_metrics?.map((m: string, i: number) => <span key={i} className="badge" style={{ background: 'rgba(16, 185, 129, 0.1)', color: '#34d399', borderColor: 'rgba(16, 185, 129, 0.3)' }}>{m}</span>)}
              </div>
            </Collapsible>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <Collapsible title="Strengths & Limitations" defaultOpen={true} icon={AlertTriangle}>
                <div style={{ marginBottom: '1rem' }}>
                  <strong style={{ color: '#34d399' }}>Strengths:</strong>
                  <ul style={{ paddingLeft: '1.5rem', marginTop: '0.5rem' }}>
                     {result.strengths?.map((s: string, i: number) => <li key={i}>{s}</li>)}
                  </ul>
                </div>
                <div>
                  <strong style={{ color: '#f87171' }}>Limitations:</strong>
                  <ul style={{ paddingLeft: '1.5rem', marginTop: '0.5rem' }}>
                     {result.limitations?.map((s: string, i: number) => <li key={i}>{s}</li>)}
                  </ul>
                </div>
              </Collapsible>
              
              <Collapsible title="Future Work" defaultOpen={false} icon={Lightbulb}>
                 <ul style={{ paddingLeft: '1.5rem' }}>
                   {result.future_work?.map((f: string, i: number) => <li key={i}>{f}</li>)}
                 </ul>
              </Collapsible>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
