import React from 'react';
import { Activity, Check, Minus, AlertTriangle, ArrowDown } from 'lucide-react';

export default function ExecutionTrace({ trace }) {
  if (!trace || trace.length === 0) return null;

  return (
    <div className="card">
      <div className="card-title">
        <Activity size={18} style={{ color: 'var(--emerald-accent)' }} />
        Agent Execution Trace Flow
      </div>

      <div className="trace-flow">
        {trace.map((step, idx) => {
          let statusClass = 'icon-completed';
          let iconNode = <Check size={14} />;

          if (step.status === 'skipped') {
            statusClass = 'icon-skipped';
            iconNode = <Minus size={14} />;
          } else if (step.status === 'fallback') {
            statusClass = 'icon-fallback';
            iconNode = <AlertTriangle size={14} />;
          }

          return (
            <React.Fragment key={idx}>
              <div className="trace-step">
                <div className="trace-step-left">
                  <div className={`status-icon ${statusClass}`}>
                    {iconNode}
                  </div>
                  <div>
                    <div style={{ fontWeight: '600', fontSize: '0.88rem' }}>{step.step}</div>
                    <div className="trace-details">{step.details}</div>
                  </div>
                </div>

                <div className="trace-latency">
                  {step.latency_ms > 0 ? `${step.latency_ms} ms` : '0 ms'}
                </div>
              </div>

              {idx < trace.length - 1 && (
                <div style={{ display: 'flex', justifyContent: 'center', margin: '-0.25rem 0', opacity: 0.3 }}>
                  <ArrowDown size={14} />
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
