import React from 'react';
import { BarChart3, TrendingDown, Zap, DollarSign, Gauge, ShieldCheck, Search, Calculator, Cpu, CheckCircle, XCircle } from 'lucide-react';

export default function BenchmarkDashboard({ benchmarkData }) {
  if (!benchmarkData) return null;

  const { results, provider, runs_per_task, pricing_model } = benchmarkData;

  const totals = results.reduce((acc, r) => {
    const c = r.comparison;
    acc.totalNaiveTokens += r.baseline_naive.metrics.total_estimated_tokens;
    acc.totalJevTokens += r.optimized_jev.metrics.total_estimated_tokens;
    acc.totalNaiveLatency += r.baseline_naive.metrics.latency_ms;
    acc.totalJevLatency += r.optimized_jev.metrics.latency_ms;
    acc.totalLLMCallsAvoided += c.llm_calls_avoided;
    acc.totalToolCallsAvoided += c.tool_calls_avoided;
    acc.totalCostSaved += c.estimated_cost_saved_usd;
    acc.totalNaiveLLMCalls += r.baseline_naive.metrics.groq_calls;
    acc.totalJevLLMCalls += r.optimized_jev.metrics.groq_calls;
    acc.totalNaiveToolCalls += r.baseline_naive.metrics.tool_calls;
    acc.totalJevToolCalls += r.optimized_jev.metrics.tool_calls;
    return acc;
  }, {
    totalNaiveTokens: 0, totalJevTokens: 0,
    totalNaiveLatency: 0, totalJevLatency: 0,
    totalLLMCallsAvoided: 0, totalToolCallsAvoided: 0,
    totalCostSaved: 0,
    totalNaiveLLMCalls: 0, totalJevLLMCalls: 0,
    totalNaiveToolCalls: 0, totalJevToolCalls: 0
  });

  const overallTokenReduction = totals.totalNaiveTokens > 0
    ? ((totals.totalNaiveTokens - totals.totalJevTokens) / totals.totalNaiveTokens * 100).toFixed(1)
    : '0.0';

  const overallLatencyReduction = totals.totalNaiveLatency > 0
    ? ((totals.totalNaiveLatency - totals.totalJevLatency) / totals.totalNaiveLatency * 100).toFixed(1)
    : '0.0';

  const costSaved10k = (totals.totalCostSaved * 10000).toFixed(2);

  const formatMs = (ms) => {
    if (ms === 0 || ms === 0.0) return '< 0.5 ms';
    if (ms < 1.0) return `${ms.toFixed(1)} ms`;
    return `${ms.toFixed(1)} ms`;
  };

  const getCategoryIcon = (category) => {
    if (category.includes('Calculator') || category.includes('Calculation')) return <Calculator size={14} />;
    if (category.includes('External') || category.includes('Search') || category.includes('Live')) return <Search size={14} />;
    if (category.includes('Code') || category.includes('Architecture')) return <Cpu size={14} />;
    return <Zap size={14} />;
  };

  return (
    <div className="card" id="benchmark-dashboard">
      <div className="card-title" style={{ marginBottom: '1.25rem' }}>
        <BarChart3 size={20} style={{ color: 'var(--primary)' }} />
        Full Benchmark Suite — All 5 Categories
        <span style={{
          marginLeft: 'auto',
          fontSize: '0.75rem',
          color: 'var(--text-muted)',
          fontWeight: '400',
          fontFamily: 'var(--font-mono)'
        }}>
          Provider: {provider.toUpperCase()} · {runs_per_task} run{runs_per_task > 1 ? 's' : ''}/task
        </span>
      </div>

      <div className="savings-banner">
        <div className="savings-stat">
          <div className="savings-num">{overallTokenReduction}%</div>
          <div className="savings-label">Overall Token Reduction</div>
        </div>
        <div className="savings-stat">
          <div className="savings-num">{overallLatencyReduction}%</div>
          <div className="savings-label">Overall Latency Reduction</div>
        </div>
        <div className="savings-stat">
          <div className="savings-num">{totals.totalLLMCallsAvoided}</div>
          <div className="savings-label">LLM Calls Avoided</div>
        </div>
        <div className="savings-stat">
          <div className="savings-num">{totals.totalToolCallsAvoided}</div>
          <div className="savings-label">Tool Calls Avoided</div>
        </div>
        <div className="savings-stat">
          <div className="savings-num" style={{ color: 'var(--cyan-accent)' }}>
            ~${costSaved10k}
          </div>
          <div className="savings-label">Est. Savings / 10k Requests</div>
        </div>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '0.75rem',
        marginBottom: '1.5rem'
      }}>
        <div className="benchmark-aggregate-box">
          <div className="benchmark-aggregate-label">Total Naive Tokens</div>
          <div className="benchmark-aggregate-value" style={{ color: 'var(--rose-accent)' }}>
            {totals.totalNaiveTokens}
          </div>
        </div>
        <div className="benchmark-aggregate-box">
          <div className="benchmark-aggregate-label">Total Jev Tokens</div>
          <div className="benchmark-aggregate-value" style={{ color: 'var(--emerald-accent)' }}>
            {totals.totalJevTokens}
          </div>
        </div>
        <div className="benchmark-aggregate-box">
          <div className="benchmark-aggregate-label">Total Naive Latency</div>
          <div className="benchmark-aggregate-value" style={{ color: 'var(--rose-accent)' }}>
            {formatMs(totals.totalNaiveLatency)}
          </div>
        </div>
        <div className="benchmark-aggregate-box">
          <div className="benchmark-aggregate-label">Total Jev Latency</div>
          <div className="benchmark-aggregate-value" style={{ color: 'var(--emerald-accent)' }}>
            {formatMs(totals.totalJevLatency)}
          </div>
        </div>
      </div>

      <div style={{ marginBottom: '0.75rem', fontSize: '0.9rem', fontWeight: '600', color: '#fff' }}>
        Per-Category Breakdown
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        {results.map((r, idx) => {
          const naive = r.baseline_naive;
          const jev = r.optimized_jev;
          const comp = r.comparison;
          const decision = jev.jev_decision;

          const tokenPct = comp.token_reduction_percentage ?? 0;
          const latencyPct = comp.latency_change_percentage ?? 0;

          const maxTokens = Math.max(1, naive.metrics.total_estimated_tokens, jev.metrics.total_estimated_tokens);
          const naiveBarW = Math.min(100, Math.max(8, (naive.metrics.total_estimated_tokens / maxTokens) * 100));
          const jevBarW = Math.min(100, Math.max(3, (jev.metrics.total_estimated_tokens / maxTokens) * 100));

          const maxLat = Math.max(1, naive.metrics.latency_ms, jev.metrics.latency_ms);
          const naiveLatW = Math.min(100, Math.max(8, (naive.metrics.latency_ms / maxLat) * 100));
          const jevLatW = Math.min(100, Math.max(3, (jev.metrics.latency_ms / maxLat) * 100));

          return (
            <div key={idx} className="benchmark-category-card">
              <div className="benchmark-category-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <div className="benchmark-category-icon">
                    {getCategoryIcon(r.task)}
                  </div>
                  <div>
                    <div style={{ fontWeight: '600', fontSize: '0.88rem' }}>Category {String.fromCharCode(65 + idx)}</div>
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', maxWidth: '400px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {r.task}
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '1.1rem', fontWeight: '700', fontFamily: 'var(--font-mono)', color: tokenPct >= 50 ? 'var(--emerald-accent)' : tokenPct > 0 ? 'var(--cyan-accent)' : 'var(--text-muted)' }}>
                      {tokenPct}%
                    </div>
                    <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>Token Savings</div>
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '1.1rem', fontWeight: '700', fontFamily: 'var(--font-mono)', color: latencyPct >= 30 ? 'var(--emerald-accent)' : latencyPct > 0 ? 'var(--cyan-accent)' : 'var(--text-muted)' }}>
                      {latencyPct}%
                    </div>
                    <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>Faster</div>
                  </div>
                </div>
              </div>

              <div className="benchmark-category-body">
                <div className="benchmark-bars-section">
                  <div style={{ marginBottom: '0.5rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '0.2rem' }}>
                      <span>Tokens</span>
                      <span>
                        <span style={{ color: 'var(--rose-accent)' }}>{naive.metrics.total_estimated_tokens}</span>
                        {' → '}
                        <span style={{ color: 'var(--emerald-accent)' }}>{jev.metrics.total_estimated_tokens}</span>
                      </span>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                      <div style={{ height: '6px', background: 'rgba(255,255,255,0.05)', borderRadius: '3px', overflow: 'hidden' }}>
                        <div style={{ width: `${naiveBarW}%`, background: 'var(--rose-accent)', height: '100%', borderRadius: '3px' }} />
                      </div>
                      <div style={{ height: '6px', background: 'rgba(255,255,255,0.05)', borderRadius: '3px', overflow: 'hidden' }}>
                        <div style={{ width: `${jevBarW}%`, background: 'var(--emerald-accent)', height: '100%', borderRadius: '3px' }} />
                      </div>
                    </div>
                  </div>

                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '0.2rem' }}>
                      <span>Latency</span>
                      <span>
                        <span style={{ color: 'var(--rose-accent)' }}>{formatMs(naive.metrics.latency_ms)}</span>
                        {' → '}
                        <span style={{ color: 'var(--emerald-accent)' }}>{formatMs(jev.metrics.latency_ms)}</span>
                      </span>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                      <div style={{ height: '6px', background: 'rgba(255,255,255,0.05)', borderRadius: '3px', overflow: 'hidden' }}>
                        <div style={{ width: `${naiveLatW}%`, background: 'rgba(244, 63, 94, 0.7)', height: '100%', borderRadius: '3px' }} />
                      </div>
                      <div style={{ height: '6px', background: 'rgba(255,255,255,0.05)', borderRadius: '3px', overflow: 'hidden' }}>
                        <div style={{ width: `${jevLatW}%`, background: 'var(--cyan-accent)', height: '100%', borderRadius: '3px' }} />
                      </div>
                    </div>
                  </div>
                </div>

                <div className="benchmark-decision-section">
                  <div className="benchmark-decision-row">
                    <span>LLM Calls</span>
                    <span style={{ fontFamily: 'var(--font-mono)' }}>
                      <span style={{ color: 'var(--rose-accent)' }}>{naive.metrics.groq_calls}</span>
                      {' → '}
                      <span style={{ color: jev.metrics.groq_calls === 0 ? 'var(--emerald-accent)' : '#fff' }}>
                        {jev.metrics.groq_calls}{jev.metrics.groq_calls === 0 ? ' ✓' : ''}
                      </span>
                    </span>
                  </div>
                  <div className="benchmark-decision-row">
                    <span>Tool Calls</span>
                    <span style={{ fontFamily: 'var(--font-mono)' }}>
                      <span style={{ color: 'var(--rose-accent)' }}>{naive.metrics.tool_calls}</span>
                      {' → '}
                      <span style={{ color: 'var(--emerald-accent)' }}>{jev.metrics.tool_calls}</span>
                    </span>
                  </div>
                  <div className="benchmark-decision-row">
                    <span>Required Tool</span>
                    <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--cyan-accent)', textTransform: 'uppercase', fontSize: '0.72rem' }}>
                      {decision.required_tool}
                    </span>
                  </div>
                  <div className="benchmark-decision-row">
                    <span>Complexity</span>
                    <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--cyan-accent)' }}>
                      {decision.task_complexity.toFixed(2)}
                    </span>
                  </div>
                  <div className="benchmark-decision-row">
                    <span>Needs External Info</span>
                    <span>
                      {decision.needs_external_information
                        ? <CheckCircle size={13} style={{ color: 'var(--emerald-accent)' }} />
                        : <XCircle size={13} style={{ color: 'var(--text-dim)' }} />
                      }
                    </span>
                  </div>
                  <div className="benchmark-decision-row">
                    <span>Needs Verification</span>
                    <span>
                      {decision.needs_verification
                        ? <CheckCircle size={13} style={{ color: 'var(--emerald-accent)' }} />
                        : <XCircle size={13} style={{ color: 'var(--text-dim)' }} />
                      }
                    </span>
                  </div>
                  <div className="benchmark-decision-row">
                    <span>Needs LLM</span>
                    <span>
                      {decision.needs_llm
                        ? <CheckCircle size={13} style={{ color: 'var(--amber-accent)' }} />
                        : <XCircle size={13} style={{ color: 'var(--emerald-accent)' }} />
                      }
                    </span>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {pricing_model && (
        <div style={{
          marginTop: '1rem',
          fontSize: '0.72rem',
          color: 'var(--text-dim)',
          fontFamily: 'var(--font-mono)',
          textAlign: 'center'
        }}>
          Pricing: Input ${pricing_model.input_price_per_1k}/1k tokens · Output ${pricing_model.output_price_per_1k}/1k tokens
        </div>
      )}
    </div>
  );
}
