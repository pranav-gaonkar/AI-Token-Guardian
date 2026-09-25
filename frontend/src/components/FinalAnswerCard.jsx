import React from 'react';
import { Terminal, Calculator, Search } from 'lucide-react';

export default function FinalAnswerCard({ result, toolResults }) {
  if (!result) return null;

  return (
    <div className="card">
      <div className="card-title">
        <Terminal size={18} style={{ color: 'var(--primary)' }} />
        Final Agent Answer & Execution Output
      </div>

      {toolResults && toolResults.calculator && (
        <div style={{
          background: 'rgba(99, 102, 241, 0.08)',
          border: '1px solid rgba(99, 102, 241, 0.2)',
          borderRadius: '8px',
          padding: '0.75rem 1rem',
          marginBottom: '1rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: '600', fontSize: '0.85rem', color: 'var(--primary)' }}>
            <Calculator size={16} />
            Calculator Output
          </div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.9rem', marginTop: '0.25rem', color: '#fff' }}>
            {toolResults.calculator.formatted_result || toolResults.calculator.error}
          </div>
        </div>
      )}

      {toolResults && toolResults.web_search && (
        <div style={{
          background: 'rgba(6, 182, 212, 0.08)',
          border: '1px solid rgba(6, 182, 212, 0.2)',
          borderRadius: '8px',
          padding: '0.75rem 1rem',
          marginBottom: '1rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyBetween: 'space-between', gap: '0.5rem', fontWeight: '600', fontSize: '0.85rem', color: 'var(--cyan-accent)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Search size={16} />
              Web Search Result
            </div>
            {toolResults.web_search.is_simulated && (
              <span style={{ fontSize: '0.75rem', background: 'rgba(245, 158, 11, 0.2)', color: 'var(--amber-accent)', padding: '0.1rem 0.5rem', borderRadius: '10px' }}>
                Demo search result
              </span>
            )}
          </div>
          <div style={{ fontSize: '0.82rem', marginTop: '0.5rem', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            {toolResults.web_search.results?.map((res, i) => (
              <div key={i} style={{ borderLeft: '2px solid var(--cyan-accent)', paddingLeft: '0.5rem' }}>
                <strong style={{ color: '#fff' }}>{res.title}:</strong> {res.snippet}
              </div>
            ))}
          </div>
        </div>
      )}

      {(result.execution_plan?.use_llm || (!toolResults?.calculator && !toolResults?.web_search)) && (
        <div className="output-box">
          {result.final_answer}
        </div>
      )}
    </div>
  );
}
