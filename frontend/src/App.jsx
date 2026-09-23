import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import TaskInput from './components/TaskInput';
import DecisionCard from './components/DecisionCard';
import ExecutionTrace from './components/ExecutionTrace';
import FinalAnswerCard from './components/FinalAnswerCard';
import MetricsComparison from './components/MetricsComparison';
import { checkHealth, fetchExamples, runAgentTask, compareAgentTask } from './services/api';

export default function App() {
  const [task, setTask] = useState('Calculate 27 * 43.');
  const [provider, setProvider] = useState('frontier_sim');
  const [healthConfig, setHealthConfig] = useState(null);
  const [examples, setExamples] = useState([]);
  const [loadingMode, setLoadingMode] = useState(null);
  const [error, setError] = useState(null);

  const [runResult, setRunResult] = useState(null);
  const [comparisonResult, setComparisonResult] = useState(null);

  useEffect(() => {
    checkHealth()
      .then((data) => setHealthConfig(data.config))
      .catch((err) => console.warn('Health check warning:', err));

    fetchExamples()
      .then(setExamples)
      .catch((err) => console.warn('Examples load warning:', err));
  }, []);

  const handleRun = async () => {
    if (!task.trim()) return;
    setLoadingMode('run');
    setError(null);
    setComparisonResult(null);

    try {
      const res = await runAgentTask(task, provider);
      setRunResult(res);
    } catch (err) {
      setError(err.message || 'Error running task');
    } finally {
      setLoadingMode(null);
    }
  };

  const handleCompare = async () => {
    if (!task.trim()) return;
    setLoadingMode('compare');
    setError(null);

    try {
      const res = await compareAgentTask(task, provider);
      setComparisonResult(res);
      setRunResult(res.optimized_jev);
    } catch (err) {
      setError(err.message || 'Error running comparison');
    } finally {
      setLoadingMode(null);
    }
  };

  return (
    <div className="container">
      <Header healthConfig={healthConfig} />

      <main>
        <TaskInput
          task={task}
          setTask={setTask}
          provider={provider}
          setProvider={setProvider}
          onRun={handleRun}
          onCompare={handleCompare}
          examples={examples}
          loadingMode={loadingMode}
        />

        {error && (
          <div className="card" style={{
            background: 'rgba(244, 63, 94, 0.1)',
            borderColor: 'rgba(244, 63, 94, 0.4)',
            color: 'var(--rose-accent)'
          }}>
            <strong>Error:</strong> {error}
          </div>
        )}

        {comparisonResult && (
          <MetricsComparison comparisonData={comparisonResult} />
        )}

        {runResult && (
          <div className="grid-2col">
            <div>
              <DecisionCard decision={runResult.jev_decision} />
              <ExecutionTrace trace={runResult.trace} />
            </div>

            <div>
              <FinalAnswerCard
                result={runResult}
                toolResults={runResult.tool_results}
              />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
