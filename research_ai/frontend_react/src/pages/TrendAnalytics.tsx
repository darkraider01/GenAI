import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { TrendingUp, Loader2 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import ReactMarkdown from 'react-markdown';

export default function TrendAnalytics() {
  const [trends, setTrends] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchTrends = async () => {
    setLoading(true);
    try {
      const res = await axios.get('http://localhost:8000/api/trends');
      setTrends(res.data);
    } catch (err) {
      console.error(err);
      alert('Failed to fetch trends');
    }
    setLoading(false);
  };

  const getBarColor = (type: string) => {
    switch(type) {
      case 'Breakthrough Topic': return '#a855f7';
      case 'Emerging Trend': return '#10b981';
      case 'Mature': return '#3b82f6';
      case 'Declining Topic': return '#ef4444';
      default: return '#94a3b8';
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem' }}>
        <div>
          <h1 style={{ display: 'flex', alignItems: 'center', gap: '1rem', margin: 0 }}>
            <TrendingUp color="#10b981" size={32} />
            Trend Analytics
          </h1>
          <p style={{ color: 'var(--text-muted)', marginTop: '0.5rem' }}>
            Identify temporal evolution patterns, methodological shifts, and breakthrough research concepts.
          </p>
        </div>
        <button className="btn" onClick={fetchTrends} disabled={loading}>
          {loading ? <Loader2 className="animate-spin" /> : 'Run Baseline Analysis'}
        </button>
      </div>

      {trends.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          <div className="glass-card" style={{ height: '400px', padding: '1rem' }}>
             <ResponsiveContainer width="100%" height="100%">
                <BarChart data={trends} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="topic_name" tick={{fill: '#94a3b8', fontSize: 12}} />
                  <YAxis yAxisId="left" orientation="left" stroke="#94a3b8" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: 'white' }}
                  />
                  <Bar yAxisId="left" dataKey="growth_rate" name="Momentum (Slope)">
                    {trends.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={getBarColor(entry.trend_type || '')} />
                    ))}
                  </Bar>
                </BarChart>
             </ResponsiveContainer>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
             <h2 style={{ fontSize: '1.2rem', margin: 0 }}>Detailed Landscape Reports</h2>
             {trends.map((t, i) => (
                <div key={i} className="collapsible">
                  <div className="collapsible-header" style={{ padding: '1.25rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                      <span style={{ fontSize: '1.25rem', fontWeight: 600, color: 'white' }}>{i + 1}. {t.topic_name}</span>
                      <span className="badge" style={{ margin: 0, border: `1px solid ${getBarColor(t.trend_type)}`, color: getBarColor(t.trend_type) }}>
                        {t.trend_type || 'Unknown'}
                      </span>
                    </div>
                  </div>
                  <div className="collapsible-content markdown-body" style={{ background: 'rgba(15, 23, 42, 0.6)' }}>
                     {t.insight_report ? (
                       <ReactMarkdown>{t.insight_report}</ReactMarkdown>
                     ) : (
                       <div>
                         <p><strong>Growth Rate:</strong> {t.growth_rate}</p>
                         <p><strong>Total Papers:</strong> {t.papers_in_topic}</p>
                       </div>
                     )}
                  </div>
                </div>
             ))}
          </div>
        </div>
      )}
    </div>
  );
}
