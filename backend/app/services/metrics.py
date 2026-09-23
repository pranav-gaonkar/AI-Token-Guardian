from typing import Optional
from app.models import AgentRunResult, MetricStats, ComparisonMetrics

def calculate_comparison_metrics(
    naive_result: AgentRunResult,
    jev_result: AgentRunResult
) -> ComparisonMetrics:
    n_m = naive_result.metrics
    j_m = jev_result.metrics

    llm_avoided = max(0, n_m.groq_calls - j_m.groq_calls)
    tool_avoided = max(0, n_m.tool_calls - j_m.tool_calls)

    token_saved = n_m.total_estimated_tokens - j_m.total_estimated_tokens
    if n_m.total_estimated_tokens > 0:
        token_reduction_pct = round(((n_m.total_estimated_tokens - j_m.total_estimated_tokens) / n_m.total_estimated_tokens) * 100.0, 2)
    else:
        token_reduction_pct = None

    latency_diff_ms = round(n_m.latency_ms - j_m.latency_ms, 2)
    if n_m.latency_ms > 0:
        latency_reduction_pct = round(((n_m.latency_ms - j_m.latency_ms) / n_m.latency_ms) * 100.0, 2)
    else:
        latency_reduction_pct = None

    return ComparisonMetrics(
        llm_calls_avoided=llm_avoided,
        tool_calls_avoided=tool_avoided,
        token_saved=token_saved if token_saved > 0 else 0,
        token_reduction_percentage=token_reduction_pct,
        latency_diff_ms=latency_diff_ms,
        latency_reduction_percentage=latency_reduction_pct
    )
