import React from 'react';
import { ShieldCheck, Cpu, Key, AlertCircle } from 'lucide-react';

export default function Header({ healthConfig }) {
  const hasJev = healthConfig?.has_openjev_key;
  const hasGroq = healthConfig?.has_groq_key;
  const hasOpenAI = healthConfig?.has_openai_key;

  let llmLabel = 'Synthetic Mode';
  let llmActive = false;

  if (hasOpenAI) {
    llmLabel = `OpenAI: ${healthConfig?.openai_model || 'gpt-4o-mini'}`;
    llmActive = true;
  } else if (hasGroq) {
    llmLabel = `Groq LLM: ${healthConfig?.groq_model || 'Active'}`;
    llmActive = true;
  }

  return (
    <header className="header">
      <div className="header-top">
        <div className="brand">
          <div className="brand-icon">
            <ShieldCheck size={26} />
          </div>
          <div className="title-group">
            <h1>AI Token Guardian</h1>
            <div className="subtitle">
              Decision-driven AI agent optimization using OpenJEV
            </div>
          </div>
        </div>

        <div className="status-badges">
          <div className={`badge ${hasJev ? 'badge-active' : 'badge-inactive'}`}>
            <Key size={12} />
            OpenJEV: {hasJev ? 'Configured' : 'Fallback Mode (No Key)'}
          </div>
          <div className={`badge ${llmActive ? 'badge-active' : 'badge-inactive'}`}>
            <Cpu size={12} />
            {llmLabel}
          </div>
        </div>
      </div>
    </header>
  );
}
