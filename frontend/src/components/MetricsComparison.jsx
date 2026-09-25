import React, { useState } from 'react';
import { BarChart3, TrendingDown, DollarSign, Share2, Check, Zap } from 'lucide-react';

export default function MetricsComparison({ comparisonData }) {
  const [copied, setCopied] = useState(false);

  if (!comparisonData) return null;

  const { task, baseline_naive, optimized_jev, comparison } = comparisonData;
  const naive = baseline_naive.metrics;
  const jev = optimized_jev.metrics;

  const costSaved10k = comparison.estimated_cost_saved_10k_usd || (comparison.token_saved * 0.1).toFixed(2);
  const tokenRedPct = comparison.token_reduction_percentage ?? 0;

  const handleCopyPost = () => {
    const postText = 
`🚀 AI Token Guardian Benchmark Result

Task: "${task}"

📊 Performance Comparison:
❌ Naive Baseline Agent:
   - LLM Calls: ${naive.groq_calls}
   - Estimated Tokens: ${naive.total_estimated_tokens}
   - Latency: ${naive.latency_ms} ms

✅ JEV Decision Agent (Bounded):
   - LLM Calls: ${jev.groq_calls} ${jev.groq_calls === 0 ? '(Avoided!)' : ''}
   - Estimated Tokens: ${jev.total_estimated_tokens}
   - Latency: ${jev.latency_ms} ms

💡 Efficiency Gains:
   - Token Reduction: ${tokenRedPct}%
   - LLM Calls Avoided: ${comparison.llm_calls_avoided}
   - Estimated Cost Savings: ~$${costSaved10k} per 10k requests!

Built using System One JEV Decision Framework + Multi-Provider LLM Router (Groq / Gemini / OpenAI).
🔗 GitHub: https://github.com/pranav-gaonkar/AI-Token-Guardian`;

    navigator.clipboard.writeText(postText);
    setCopied(true);
    setTimeout(() => setCopied(false), 3000);
  };

  const formatMs = (ms) => {
    if (ms === 0 || ms === 0.0) return '< 0.5 ms';
    if (ms < 1.0) return `${ms.toFixed(1)} ms`;
    return `${ms} ms`;
  };

  const maxTokens = Math.max(1, naive.total_estimated_tokens, jev.total_estimated_tokens);
  const naiveTokenWidth = Math.min(100, Math.max(10, (naive.total_estimated_tokens / maxTokens) * 100));
  const jevTokenWidth = Math.min(100, Math.max(5, (jev.total_estimated_tokens / maxTokens) * 100));

  const maxLatency = Math.max(1, naive.latency_ms, jev.latency_ms);
  const naiveLatencyWidth = Math.min(100, Math.max(10, (naive.latency_ms / maxLatency) * 100));
  const jevLatencyWidth = Math.min(100, Math.max(5, (jev.latency_ms / maxLatency) * 100));

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem', marginBottom: '1rem' }}>
        <div className="card-title" style={{ margin: 0 }}>
          <BarChart3 size={18} style={{ color: 'var(--emerald-accent)' }} />
          Measured Comparison: Naive Baseline vs Jev Decision Agent
        </div>

        <button
          type="button"
          className="pill-btn"
          onClick={handleCopyPost}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.4rem',
            background: copied ? 'rgba(16, 185, 129, 0.2)' : 'rgba(99, 102, 241, 0.15)',
            borderColor: copied ? 'var(--emerald-accent)' : 'var(--border-highlight)',
            color: copied ? 'var(--emerald-accent)' : '#fff',
            fontWeight: '600',
            padding: '0.4rem 0.85rem'
          }}
        >
          {copied ? <Check size={14} /> : <Share2 size={14} />}
          {copied ? 'Copied LinkedIn Snippet!' : 'Copy LinkedIn Post Snippet'}
        </button>
      </div>

      <div className="savings-banner">
        <div className="savings-stat">
          <div className="savings-num">{comparison.llm_calls_avoided}</div>
          <div className="savings-label">LLM Calls Avoided</div>
        </div>

        <div className="savings-stat">
          <div className="savings-num">{comparison.tool_calls_avoided}</div>
          <div className="savings-label">Tool Calls Avoided</div>
        </div>

        <div className="savings-stat">
          <div className="savings-num">
            {tokenRedPct}%
          </div>
          <div className="savings-label">Token Reduction</div>
        </div>

        <div className="savings-stat">
          <div className="savings-num" style={{ color: 'var(--cyan-accent)' }}>
            ~${costSaved10k}
          </div>
          <div className="savings-label">Est. Savings / 10k Requests</div>
        </div>
      </div>

      <div style={{
        background: 'rgba(0, 0, 0, 0.2)',
        border: '1px solid var(--border-color)',
        borderRadius: '10px',
        padding: '1rem',
        marginBottom: '1.5rem'
      }}>
        <div style={{ fontSize: '0.85rem', fontWeight: '600', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
          📊 Visual Metrics Breakdown
        </div>

        <div style={{ marginBottom: '0.75rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: '0.25rem' }}>
            <span>Total Estimated Tokens</span>
            <span>Naive: <strong>{naive.total_estimated_tokens}</strong> vs Jev: <strong style={{ color: 'var(--emerald-accent)' }}>{jev.total_estimated_tokens}</strong></span>
          </div>
          <div style={{ height: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', overflow: 'hidden', display: 'flex', gap: '2px' }}>
            <div style={{ width: `${naiveTokenWidth}%`, background: 'var(--rose-accent)', height: '100%', borderRadius: '4px' }} title={`Naive Tokens: ${naive.total_estimated_tokens}`}></div>
          </div>
          <div style={{ height: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', overflow: 'hidden', marginTop: '4px' }}>
            <div style={{ width: `${jevTokenWidth}%`, background: 'var(--emerald-accent)', height: '100%', borderRadius: '4px' }} title={`Jev Tokens: ${jev.total_estimated_tokens}`}></div>
          </div>
        </div>

        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: '0.25rem' }}>
            <span>Execution Latency (ms)</span>
            <span>Naive: <strong>{formatMs(naive.latency_ms)}</strong> vs Jev: <strong style={{ color: 'var(--cyan-accent)' }}>{formatMs(jev.latency_ms)}</strong></span>
          </div>
          <div style={{ height: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', overflow: 'hidden' }}>
            <div style={{ width: `${naiveLatencyWidth}%`, background: 'rgba(244, 63, 94, 0.7)', height: '100%', borderRadius: '4px' }} title={`Naive Latency: ${formatMs(naive.latency_ms)}`}></div>
          </div>
          <div style={{ height: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', overflow: 'hidden', marginTop: '4px' }}>
            <div style={{ width: `${jevLatencyWidth}%`, background: 'var(--cyan-accent)', height: '100%', borderRadius: '4px' }} title={`Jev Latency: ${formatMs(jev.latency_ms)}`}></div>
          </div>
        </div>
      </div>

      <div className="comparison-container">
        <div className="comp-card comp-card-naive">
          <div className="comp-header">
            <h3 style={{ fontSize: '1rem', color: 'var(--rose-accent)' }}>Naive Baseline Agent</h3>
            <span className="badge badge-inactive">Unbounded</span>
          </div>

          <div className="comp-metrics-list">
            <div className="comp-metric-row">
              <span>OpenJEV Calls:</span>
              <span>{naive.openjev_calls}</span>
            </div>
            <div className="comp-metric-row">
              <span>Groq / LLM Calls:</span>
              <span style={{ color: 'var(--rose-accent)', fontWeight: 'bold' }}>{naive.groq_calls}</span>
            </div>
            <div className="comp-metric-row">
              <span>Tool Calls Executed:</span>
              <span>{naive.tool_calls}</span>
            </div>
            <div className="comp-metric-row">
              <span>Input Tokens (Est):</span>
              <span>{naive.estimated_input_tokens}</span>
            </div>
            <div className="comp-metric-row">
              <span>Output Tokens (Est):</span>
              <span>{naive.estimated_output_tokens}</span>
            </div>
            <div className="comp-metric-row" style={{ borderBottom: 'none', fontWeight: 'bold' }}>
              <span>Total Estimated Tokens:</span>
              <span style={{ color: 'var(--rose-accent)' }}>{naive.total_estimated_tokens}</span>
            </div>
            <div className="comp-metric-row" style={{ borderBottom: 'none', color: 'var(--text-muted)' }}>
              <span>Total Latency:</span>
              <span>{formatMs(naive.latency_ms)}</span>
            </div>
          </div>
        </div>

        <div className="comp-card comp-card-jev">
          <div className="comp-header">
            <h3 style={{ fontSize: '1rem', color: 'var(--emerald-accent)' }}>Jev Decision Agent</h3>
            <span className="badge badge-active">Decision Bounded</span>
          </div>

          <div className="comp-metrics-list">
            <div className="comp-metric-row">
              <span>OpenJEV Calls:</span>
              <span style={{ color: 'var(--cyan-accent)' }}>{jev.openjev_calls}</span>
            </div>
            <div className="comp-metric-row">
              <span>Groq / LLM Calls:</span>
              <span style={{ color: jev.groq_calls === 0 ? 'var(--emerald-accent)' : '#fff', fontWeight: 'bold' }}>
                {jev.groq_calls} {jev.groq_calls === 0 ? '(Avoided!)' : ''}
              </span>
            </div>
            <div className="comp-metric-row">
              <span>Tool Calls Executed:</span>
              <span>{jev.tool_calls}</span>
            </div>
            <div className="comp-metric-row">
              <span>Input Tokens (Est):</span>
              <span>{jev.estimated_input_tokens}</span>
            </div>
            <div className="comp-metric-row">
              <span>Output Tokens (Est):</span>
              <span>{jev.estimated_output_tokens}</span>
            </div>
            <div className="comp-metric-row" style={{ borderBottom: 'none', fontWeight: 'bold' }}>
              <span>Total Estimated Tokens:</span>
              <span style={{ color: 'var(--emerald-accent)' }}>{jev.total_estimated_tokens}</span>
            </div>
            <div className="comp-metric-row" style={{ borderBottom: 'none', color: 'var(--text-muted)' }}>
              <span>Total Latency:</span>
              <span>{formatMs(jev.latency_ms)}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
