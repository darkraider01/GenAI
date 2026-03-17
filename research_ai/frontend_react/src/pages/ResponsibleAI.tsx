import React, { useState } from 'react';
import { ShieldCheck, AlertTriangle, CheckCircle, XCircle, Eye, Scale, Zap, ChevronDown, ChevronUp } from 'lucide-react';

const API = 'http://localhost:8000';

// ── Types ──────────────────────────────────────────────────────────────────
interface SafetyReport { safe: boolean; risk_level: string; reason: string; check_type: string; }
interface BiasFlag { type: string; severity: string; detail: string; }
interface BiasReport { bias_flags: BiasFlag[]; bias_score: number; bias_count: number; recommendation: string; }
interface Source { title: string; authors: string; year: string; relevance_score: number | string; }
interface TransparencyReport {
  sources_cited: number; avg_confidence: number; confidence_label: string;
  confidence_percent: number; attribution_summary: string; top_sources: Source[];
}
interface RAIReport {
  rai_status: string; rai_color: string; overall_score: number;
  safety: { input: SafetyReport; output: SafetyReport; combined_risk: number; };
  bias: BiasReport;
  transparency: TransparencyReport;
}

// ── Color helpers ──────────────────────────────────────────────────────────
const riskColor: Record<string, string> = {
  SAFE: '#10b981', LOW: '#84cc16', MEDIUM: '#f59e0b', HIGH: '#ef4444'
};
const riskBg: Record<string, string> = {
  SAFE: 'rgba(16,185,129,0.1)', LOW: 'rgba(132,204,18,0.1)',
  MEDIUM: 'rgba(245,158,11,0.1)', HIGH: 'rgba(239,68,68,0.1)'
};
const statusMeta: Record<string, { icon: React.ReactElement; color: string; bg: string; label: string }> = {
  COMPLIANT: { icon: <CheckCircle size={28} />, color: '#10b981', bg: 'rgba(16,185,129,0.12)', label: 'Compliant' },
  REVIEW_RECOMMENDED: { icon: <AlertTriangle size={28} />, color: '#f59e0b', bg: 'rgba(245,158,11,0.12)', label: 'Review Recommended' },
  NON_COMPLIANT: { icon: <XCircle size={28} />, color: '#ef4444', bg: 'rgba(239,68,68,0.12)', label: 'Non-Compliant' },
};
const severityColor: Record<string, string> = { HIGH: '#ef4444', MEDIUM: '#f59e0b', LOW: '#84cc16' };

// ── Subcomponents ──────────────────────────────────────────────────────────
function OverallBadge({ report }: { report: RAIReport }) {
  const meta = statusMeta[report.rai_status] ?? statusMeta.REVIEW_RECOMMENDED;
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: '1.5rem',
      padding: '2rem 2.5rem',
      background: meta.bg,
      border: `1px solid ${meta.color}33`,
      borderRadius: '20px',
      marginBottom: '2rem',
      animation: 'fadeIn 0.4s ease',
    }}>
      <div style={{ color: meta.color, filter: `drop-shadow(0 0 10px ${meta.color}88)` }}>{meta.icon}</div>
      <div style={{ flex: 1 }}>
        <div style={{ color: meta.color, fontWeight: 800, fontSize: '1.3rem', marginBottom: '0.25rem' }}>
          RAI Status: {meta.label}
        </div>
        <div style={{ color: '#94a3b8', fontSize: '0.95rem' }}>
          Overall Responsible AI Score: <strong style={{ color: meta.color }}>{report.overall_score} / 100</strong>
        </div>
      </div>
      {/* Score ring */}
      <div style={{ position: 'relative', width: '80px', height: '80px', flexShrink: 0 }}>
        <svg viewBox="0 0 80 80" style={{ transform: 'rotate(-90deg)' }}>
          <circle cx="40" cy="40" r="32" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="8" />
          <circle cx="40" cy="40" r="32" fill="none" stroke={meta.color}
            strokeWidth="8" strokeLinecap="round"
            strokeDasharray={`${(report.overall_score / 100) * 201} 201`}
            style={{ filter: `drop-shadow(0 0 6px ${meta.color})`, transition: 'stroke-dasharray 1s ease' }} />
        </svg>
        <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, fontSize: '1.1rem', color: meta.color }}>
          {report.overall_score}
        </div>
      </div>
    </div>
  );
}

function SafetyPanel({ safety }: { report: RAIReport; safety: RAIReport['safety'] }) {
  const inputMeta = safety.input;
  const outputMeta = safety.output;
  return (
    <div className="glass-card rai-panel">
      <div className="rai-panel-header">
        <ShieldCheck size={22} style={{ color: '#6366f1' }} />
        <h3 style={{ margin: 0, color: '#e2e8f0' }}>Content Safety</h3>
        <span className="rai-pill" style={{ background: riskBg[inputMeta.risk_level], color: riskColor[inputMeta.risk_level], borderColor: riskColor[inputMeta.risk_level] + '44' }}>
          {inputMeta.risk_level}
        </span>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '1.25rem' }}>
        {[{ label: 'Input Guardrail', d: inputMeta }, { label: 'Output Guardrail', d: outputMeta }].map(({ label, d }) => (
          <div key={label} style={{ padding: '1.25rem', background: riskBg[d.risk_level], border: `1px solid ${riskColor[d.risk_level]}33`, borderRadius: '14px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
              <span style={{ color: '#94a3b8', fontSize: '0.85rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>{label}</span>
              <span style={{ color: riskColor[d.risk_level], fontWeight: 700, fontSize: '0.85rem' }}>{d.risk_level}</span>
            </div>
            <p style={{ color: '#cbd5e1', fontSize: '0.9rem', lineHeight: 1.5, margin: 0 }}>{d.reason}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function BiasPanel({ bias }: { bias: BiasReport }) {
  const [expanded, setExpanded] = useState(true);
  const percent = Math.round(bias.bias_score * 100);
  const barColor = percent < 25 ? '#10b981' : percent < 55 ? '#f59e0b' : '#ef4444';
  return (
    <div className="glass-card rai-panel">
      <div className="rai-panel-header" style={{ cursor: 'pointer' }} onClick={() => setExpanded(e => !e)}>
        <Scale size={22} style={{ color: '#c084fc' }} />
        <h3 style={{ margin: 0, color: '#e2e8f0' }}>Bias Analysis</h3>
        <span className="rai-pill" style={{ background: 'rgba(192,132,252,0.1)', color: '#c084fc', borderColor: '#c084fc44' }}>
          {bias.bias_count} flag{bias.bias_count !== 1 ? 's' : ''}
        </span>
        <div style={{ marginLeft: 'auto', color: '#475569' }}>{expanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}</div>
      </div>

      {/* Bias meter */}
      <div style={{ marginTop: '1.25rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', fontSize: '0.85rem' }}>
          <span style={{ color: '#94a3b8' }}>Bias Score</span>
          <span style={{ color: barColor, fontWeight: 700 }}>{percent}%</span>
        </div>
        <div style={{ height: '10px', background: 'rgba(255,255,255,0.05)', borderRadius: '99px', overflow: 'hidden' }}>
          <div style={{ height: '100%', width: `${percent}%`, background: `linear-gradient(90deg, #10b981, ${barColor})`, borderRadius: '99px', transition: 'width 1s ease', boxShadow: `0 0 8px ${barColor}66` }} />
        </div>
      </div>

      {expanded && (
        <div style={{ marginTop: '1.25rem' }}>
          {bias.bias_flags.length === 0 ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '1rem', background: 'rgba(16,185,129,0.08)', borderRadius: '12px', border: '1px solid rgba(16,185,129,0.2)' }}>
              <CheckCircle size={18} style={{ color: '#10b981', flexShrink: 0 }} />
              <span style={{ color: '#94a3b8', fontSize: '0.9rem' }}>No bias flags detected. Output meets academic standards.</span>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {bias.bias_flags.map((f, i) => (
                <div key={i} style={{ padding: '1rem 1.25rem', background: `${severityColor[f.severity]}0d`, border: `1px solid ${severityColor[f.severity]}33`, borderLeft: `4px solid ${severityColor[f.severity]}`, borderRadius: '10px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                    <span style={{ color: '#e2e8f0', fontWeight: 600, fontSize: '0.95rem' }}>{f.type}</span>
                    <span style={{ color: severityColor[f.severity], fontSize: '0.8rem', fontWeight: 700 }}>{f.severity}</span>
                  </div>
                  <p style={{ color: '#94a3b8', fontSize: '0.875rem', margin: 0 }}>{f.detail}</p>
                </div>
              ))}
            </div>
          )}
          <p style={{ color: '#64748b', fontSize: '0.875rem', marginTop: '1rem', fontStyle: 'italic' }}>{bias.recommendation}</p>
        </div>
      )}
    </div>
  );
}

function TransparencyPanel({ t }: { t: TransparencyReport }) {
  const confColor = t.confidence_label === 'HIGH' ? '#10b981' : t.confidence_label === 'MEDIUM' ? '#f59e0b' : '#ef4444';
  return (
    <div className="glass-card rai-panel">
      <div className="rai-panel-header">
        <Eye size={22} style={{ color: '#38bdf8' }} />
        <h3 style={{ margin: 0, color: '#e2e8f0' }}>Transparency & Attribution</h3>
        <span className="rai-pill" style={{ background: `${confColor}18`, color: confColor, borderColor: `${confColor}44` }}>
          {t.confidence_label} confidence
        </span>
      </div>
      {/* Stats row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginTop: '1.25rem' }}>
        {[
          { label: 'Sources Cited', value: t.sources_cited, unit: 'papers' },
          { label: 'Grounding Confidence', value: `${t.confidence_percent}%`, unit: t.confidence_label },
          { label: 'RAG Attribution', value: t.sources_cited > 0 ? 'Active' : 'None', unit: 'pipeline' },
        ].map(stat => (
          <div key={stat.label} style={{ padding: '1.25rem', background: 'rgba(56,189,248,0.05)', border: '1px solid rgba(56,189,248,0.12)', borderRadius: '14px', textAlign: 'center' }}>
            <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#38bdf8', lineHeight: 1, marginBottom: '0.4rem' }}>{stat.value}</div>
            <div style={{ color: '#94a3b8', fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}>{stat.label}</div>
          </div>
        ))}
      </div>
      {/* Confidence bar */}
      <div style={{ marginTop: '1.25rem' }}>
        <div style={{ height: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '99px', overflow: 'hidden' }}>
          <div style={{ height: '100%', width: `${t.confidence_percent}%`, background: `linear-gradient(90deg, #6366f1, ${confColor})`, borderRadius: '99px', transition: 'width 1s ease', boxShadow: `0 0 8px ${confColor}55` }} />
        </div>
      </div>
      <p style={{ color: '#64748b', fontSize: '0.9rem', marginTop: '1rem', lineHeight: 1.6 }}>{t.attribution_summary}</p>

      {/* Sources table */}
      {t.top_sources.length > 0 && (
        <div style={{ marginTop: '1rem' }}>
          <div style={{ fontSize: '0.8rem', color: '#475569', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '0.75rem', fontWeight: 700 }}>Top Retrieved Sources</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {t.top_sources.map((s, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '1rem', padding: '0.75rem 1rem', background: 'rgba(15,23,42,0.5)', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.05)' }}>
                <span style={{ color: '#475569', fontSize: '0.8rem', fontWeight: 700, width: '20px', textAlign: 'center' }}>#{i + 1}</span>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ color: '#e2e8f0', fontSize: '0.875rem', fontWeight: 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{s.title}</div>
                  <div style={{ color: '#475569', fontSize: '0.8rem' }}>{s.authors} · {s.year}</div>
                </div>
                <span style={{ color: '#38bdf8', fontSize: '0.8rem', fontWeight: 700, flexShrink: 0 }}>
                  {typeof s.relevance_score === 'number' ? `${(s.relevance_score * 100).toFixed(0)}%` : 'N/A'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ── Main Page ──────────────────────────────────────────────────────────────
export default function ResponsibleAI() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<RAIReport | null>(null);
  const [error, setError] = useState('');

  const runAudit = async () => {
    if (!query.trim() || !response.trim()) {
      setError('Please provide both the original query and the AI response to audit.');
      return;
    }
    setError('');
    setLoading(true);
    setReport(null);
    try {
      const res = await fetch(`${API}/api/rai-audit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, response, papers: [] }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Audit failed.');
      setReport(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ animation: 'fadeIn 0.4s ease' }}>
      {/* Header */}
      <div style={{ marginBottom: '2.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.75rem' }}>
          <div style={{ padding: '0.75rem', background: 'rgba(16,185,129,0.12)', borderRadius: '14px', border: '1px solid rgba(16,185,129,0.25)' }}>
            <ShieldCheck size={32} style={{ color: '#10b981', filter: 'drop-shadow(0 0 10px rgba(16,185,129,0.6))' }} />
          </div>
          <div>
            <h1 style={{ margin: 0, fontSize: '2rem', background: 'linear-gradient(to right, #10b981, #38bdf8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              Ethics Shield
            </h1>
            <p style={{ margin: 0, color: '#64748b', fontSize: '0.95rem' }}>Responsible AI Auditor — Safety · Bias · Transparency</p>
          </div>
        </div>
        {/* Pillar badges */}
        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', marginTop: '1rem' }}>
          {[
            { icon: <ShieldCheck size={14} />, label: 'Content Safety', color: '#6366f1' },
            { icon: <Scale size={14} />, label: 'Bias Detection', color: '#c084fc' },
            { icon: <Eye size={14} />, label: 'Transparency', color: '#38bdf8' },
            { icon: <Zap size={14} />, label: 'Real-time Audit', color: '#10b981' },
          ].map(b => (
            <span key={b.label} style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', padding: '0.35rem 0.9rem', background: `${b.color}14`, border: `1px solid ${b.color}33`, borderRadius: '99px', color: b.color, fontSize: '0.82rem', fontWeight: 600 }}>
              {b.icon}{b.label}
            </span>
          ))}
        </div>
      </div>

      {/* Input Form */}
      <div className="glass-card">
        <h3 style={{ marginBottom: '1.25rem', color: '#94a3b8', fontSize: '0.9rem', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: 700 }}>
          Audit Configuration
        </h3>
        <label style={{ color: '#94a3b8', fontSize: '0.85rem', display: 'block', marginBottom: '0.5rem' }}>Original Research Query</label>
        <input
          className="input-field"
          placeholder="e.g. What are the latest methods in federated learning for healthcare?"
          value={query}
          onChange={e => setQuery(e.target.value)}
          style={{ marginBottom: '1.25rem' }}
        />
        <label style={{ color: '#94a3b8', fontSize: '0.85rem', display: 'block', marginBottom: '0.5rem' }}>AI-Generated Response to Audit</label>
        <textarea
          className="input-field"
          placeholder="Paste or type the AI-generated text you want to audit for safety, bias, and transparency..."
          value={response}
          onChange={e => setResponse(e.target.value)}
          rows={6}
          style={{ resize: 'vertical', marginBottom: '1.5rem', fontFamily: 'inherit' }}
        />
        {error && (
          <div style={{ padding: '0.85rem 1.25rem', background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: '10px', color: '#fca5a5', marginBottom: '1rem', fontSize: '0.9rem' }}>
            {error}
          </div>
        )}
        <button className="btn" onClick={runAudit} disabled={loading} style={{ background: 'linear-gradient(135deg, #10b981, #059669)', boxShadow: '0 10px 15px -3px rgba(16,185,129,0.3)' }}>
          {loading ? <><span className="loader" /> Running Ethics Audit…</> : <><ShieldCheck size={18} /> Run Ethics Audit</>}
        </button>
      </div>

      {/* Results */}
      {report && (
        <div style={{ animation: 'fadeIn 0.5s ease' }}>
          <OverallBadge report={report} />
          <SafetyPanel report={report} safety={report.safety} />
          <BiasPanel bias={report.bias} />
          <TransparencyPanel t={report.transparency} />
        </div>
      )}
    </div>
  );
}
