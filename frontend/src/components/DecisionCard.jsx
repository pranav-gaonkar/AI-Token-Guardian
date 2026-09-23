import React from 'react';
import { Network, AlertTriangle, CheckCircle, Info } from 'lucide-react';

export default function DecisionCard({ decision }) {
  if (!decision) return null;

  const isFallback = decision.fallback_occurred;

  return (
    <div className="card">
      <div className="card-title" style={{ justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Network size={18} style={{ color: 'var(--cyan-accent)' }} />
          Jev Decision Breakdown
        </div>

        <div style={{ fontSize: '0.75rem', fontWeight: '500', color: 'var(--text-muted)' }}>
          Source: <strong style={{ color: isFallback ? 'var(--amber-accent)' : 'var(--emerald-accent)' }}>
            {decision.decision_source}
          </strong>
        </div>
      </div>

      {isFallback && (
        <div style={{
          background: 'rgba(245, 158, 11, 0.1)',
          border: '1px solid rgba(245, 158, 11, 0.3)',
          borderRadius: '8px',
          padding: '0.6rem 0.8rem',
          marginBottom: '1rem',
          fontSize: '0.8rem',
          color: 'var(--amber-accent)',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          <AlertTriangle size={16} />
          <span>OpenJEV unavailable — fallback workflow rules applied. ({decision.fallback_reason})</span>
        </div>
      )}

      <div className="decision-grid">
        <div className="decision-item">
          <div className="decision-label">Needs External Info</div>
          <div className={`decision-val ${decision.needs_external_information ? 'val-yes' : 'val-no'}`}>
            {decision.needs_external_information ? 'YES' : 'NO'}
          </div>
        </div>

        <div className="decision-item">
          <div className="decision-label">Required Tool</div>
          <div className="decision-val val-tool">
            {decision.required_tool}
          </div>
        </div>

        <div className="decision-item">
          <div className="decision-label">Needs LLM</div>
          <div className={`decision-val ${decision.needs_llm ? 'val-yes' : 'val-no'}`}>
            {decision.needs_llm ? 'YES' : 'NO'}
          </div>
        </div>

        <div className="decision-item">
          <div className="decision-label">Needs Verification</div>
          <div className={`decision-val ${decision.needs_verification ? 'val-yes' : 'val-no'}`}>
            {decision.needs_verification ? 'YES' : 'NO'}
          </div>
        </div>

        <div className="decision-item" style={{ gridColumn: 'span 2' }}>
          <div className="decision-label">Task Complexity Score</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginTop: '0.2rem' }}>
            <div className="decision-val" style={{ color: 'var(--cyan-accent)' }}>
              {decision.task_complexity.toFixed(2)} / 1.00
            </div>
            <div style={{
              flex: 1,
              height: '6px',
              background: 'rgba(255,255,255,0.1)',
              borderRadius: '3px',
              overflow: 'hidden'
            }}>
              <div style={{
                width: `${decision.task_complexity * 100}%`,
                height: '100%',
                background: 'var(--primary-gradient)'
              }} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
