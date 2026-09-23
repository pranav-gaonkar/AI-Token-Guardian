import React from 'react';
import { Play, GitCompare, Sparkles } from 'lucide-react';

export default function TaskInput({
  task,
  setTask,
  provider,
  setProvider,
  onRun,
  onCompare,
  examples,
  loadingMode
}) {
  const isLoading = Boolean(loadingMode);

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div className="card-title" style={{ margin: 0 }}>
          <Sparkles size={18} className="text-cyan" style={{ color: 'var(--cyan-accent)' }} />
          Enter a Task for the Agent
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>LLM Baseline Speed Mode:</span>
          <select
            value={provider}
            onChange={(e) => setProvider(e.target.value)}
            disabled={isLoading}
            style={{
              background: '#0f172a',
              color: '#38bdf8',
              border: '1px solid rgba(56, 189, 248, 0.3)',
              borderRadius: '6px',
              padding: '0.3rem 0.6rem',
              fontSize: '0.85rem',
              fontWeight: '500',
              cursor: 'pointer',
              outline: 'none'
            }}
          >
            <option value="groq">⚡ Groq LPUs (Ultra-Fast Hardware Mode)</option>
            <option value="frontier_sim">🐢 Frontier LLM Benchmark (Realistic GPT-4 / Claude Speed)</option>
            <option value="gemini">🌐 Google Gemini API (Free Key Mode)</option>
            <option value="openai">💸 OpenAI GPT-4o (Paid API Key Mode)</option>
          </select>
        </div>
      </div>

      <div className="input-group">
        <textarea
          className="task-textarea"
          value={task}
          onChange={(e) => setTask(e.target.value)}
          placeholder="Should I use a calculator, search the web, or ask the LLM to answer this?"
          rows={3}
          disabled={isLoading}
        />

        {examples && examples.length > 0 && (
          <div className="examples-pills">
            <span className="examples-label">Try Example Tasks:</span>
            {examples.map((ex) => (
              <button
                key={ex.id}
                type="button"
                className="pill-btn"
                onClick={() => setTask(ex.task)}
                title={ex.description}
                disabled={isLoading}
              >
                {ex.title}
              </button>
            ))}
          </div>
        )}

        <div className="button-group">
          <button
            type="button"
            className="btn btn-primary"
            onClick={onRun}
            disabled={isLoading || !task.trim()}
          >
            {loadingMode === 'run' ? (
              <>
                <span className="spinner"></span>
                Evaluating OpenJEV Decision...
              </>
            ) : (
              <>
                <Play size={16} />
                Run Jev Agent
              </>
            )}
          </button>

          <button
            type="button"
            className="btn btn-secondary"
            onClick={onCompare}
            disabled={isLoading || !task.trim()}
          >
            {loadingMode === 'compare' ? (
              <>
                <span className="spinner"></span>
                Running Baseline Comparison...
              </>
            ) : (
              <>
                <GitCompare size={16} />
                Run Comparison (Naive vs Jev)
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
