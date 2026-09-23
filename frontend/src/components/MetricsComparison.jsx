import React from 'react';
import { BarChart3, TrendingDown, Zap, Layers, Cpu } from 'lucide-react';

export default function MetricsComparison({ comparisonData }) {
  if (!comparisonData) return null;

  const { baseline_naive, optimized_jev, comparison } = comparisonData;
  const naive = baseline_naive.metrics;
  const jev = optimized_jev.metrics;

  return (
    <div className="card">
      <div className="card-title">
        <BarChart3 size={18} style={{ color: 'var(--emerald-accent)' }} />
        Measured Comparison: Naive Baseline vs Jev Decision Agent
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
            {comparison.token_reduction_percentage !== null
              ? `${comparison.token_reduction_percentage}%`
              : '0%'}
          </div>
          <div className="savings-label">Token Reduction</div>
        </div>

        <div className="savings-stat">
          <div className="savings-num">
            {comparison.latency_diff_ms > 0 ? `-${comparison.latency_diff_ms} ms` : `${comparison.latency_diff_ms} ms`}
          </div>
          <div className="savings-label">Latency Difference</div>
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
              <span>Groq LLM Calls:</span>
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
              <span>{naive.latency_ms} ms</span>
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
              <span>Groq LLM Calls:</span>
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
              <span>{jev.latency_ms} ms</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
