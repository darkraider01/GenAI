import { useState } from 'react';
import axios from 'axios';
import { Globe, Lightbulb, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export default function LandscapePanels() {
  const [forecast, setForecast] = useState('');
  const [loadingForecast, setLoadingForecast] = useState(false);
  
  const fetchForecast = async () => {
    setLoadingForecast(true);
    try {
      const res = await axios.get('http://localhost:8000/api/forecast');
      setForecast(res.data.forecast);
    } catch(err) {
       console.error(err);
    }
    setLoadingForecast(false);
  }

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <h1 style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '2rem' }}>
        <Globe color="#14b8a6" size={32} />
        Macroscopic Intelligence
      </h1>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr)', gap: '2rem', flex: 1 }}>
        
        {/* Future Forecast Panel */}
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
           <div className="glass-card" style={{ flex: 1, display: 'flex', flexDirection: 'column', borderTop: '4px solid #8b5cf6' }}>
             <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <h2 style={{ fontSize: '1.25rem', margin: 0, border: 'none', color: 'white', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                   <Lightbulb color="#8b5cf6" size={20} />
                   3-Year Horizon Forecast
                </h2>
                <button className="btn" onClick={fetchForecast} disabled={loadingForecast} style={{ padding: '0.5rem 1rem', background: '#6d28d9' }}>
                   {loadingForecast ? <Loader2 size={16} className="animate-spin" /> : 'Predict'}
                </button>
             </div>
             
             <div className="markdown-body" style={{ flex: 1, overflowY: 'auto', paddingRight: '1rem' }}>
                {forecast ? (
                  <ReactMarkdown>{forecast}</ReactMarkdown>
                ) : (
                  <div style={{ color: 'var(--text-muted)', display: 'flex', height: '100%', alignItems: 'center', justifyContent: 'center', textAlign: 'center' }}>
                    Click Predict to extrapolate current topic momentum into a visionary AI-guided 3-year research outlook.
                  </div>
                )}
             </div>
           </div>
        </div>

      </div>
    </div>
  );
}
