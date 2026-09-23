export async function checkHealth() {
  const res = await fetch('/health');
  if (!res.ok) throw new Error('Health check failed');
  return res.json();
}

export async function fetchExamples() {
  const res = await fetch('/api/examples');
  if (!res.ok) throw new Error('Failed to fetch examples');
  return res.json();
}

export async function runAgentTask(task, provider = 'groq') {
  const res = await fetch('/api/run', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ task, provider })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'API request failed' }));
    throw new Error(err.detail || 'Failed to run task');
  }
  return res.json();
}

export async function compareAgentTask(task, provider = 'groq') {
  const res = await fetch('/api/compare', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ task, provider })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Comparison request failed' }));
    throw new Error(err.detail || 'Failed to run comparison');
  }
  return res.json();
}
