from typing import Optional, List, Dict
from app.models import AgentRunResult, MetricStats, ComparisonMetrics

MODEL_PRICING: Dict[str, Dict[str, float]] = {
    "groq": {
        "input_price_per_1k": 0.0001,
        "output_price_per_1k": 0.0002
    },
    "gemini": {
        "input_price_per_1k": 0.000075,
        "output_price_per_1k": 0.0003
    },
    "openai": {
        "input_price_per_1k": 0.00015,
        "output_price_per_1k": 0.0006
    },
    "frontier_sim": {
        "input_price_per_1k": 0.0025,
        "output_price_per_1k": 0.010
    }
}

def compute_run_cost(input_tokens: int, output_tokens: int, provider: Optional[str] = None) -> float:
    p_key = (provider or "groq").lower()
    pricing = MODEL_PRICING.get(p_key, MODEL_PRICING["groq"])
    cost = (input_tokens / 1000.0 * pricing["input_price_per_1k"]) + (output_tokens / 1000.0 * pricing["output_price_per_1k"])
    return round(cost, 6)

def aggregate_agent_results(results: List[AgentRunResult], provider: Optional[str] = None) -> AgentRunResult:
    if not results:
        raise ValueError("Cannot aggregate empty result list.")

    if len(results) == 1:
        single = results[0]
        c = compute_run_cost(single.metrics.estimated_input_tokens, single.metrics.estimated_output_tokens, provider)
        single.metrics.cost_usd = c
        return single

    first = results[0]
    latencies = [r.metrics.latency_ms for r in results]
    avg_latency = round(sum(latencies) / len(latencies), 2)
    min_lat = round(min(latencies), 2)
    max_lat = round(max(latencies), 2)

    avg_in_tokens = int(round(sum(r.metrics.estimated_input_tokens for r in results) / len(results)))
    avg_out_tokens = int(round(sum(r.metrics.estimated_output_tokens for r in results) / len(results)))
    avg_total_tokens = avg_in_tokens + avg_out_tokens

    avg_openjev_calls = round(sum(r.metrics.openjev_calls for r in results) / len(results), 2)
    avg_groq_calls = round(sum(r.metrics.groq_calls for r in results) / len(results), 2)
    avg_tool_calls = round(sum(r.metrics.tool_calls for r in results) / len(results), 2)

    fallback = any(r.metrics.fallback_occurred for r in results)
    token_src = first.metrics.token_source
    is_est = any(r.metrics.is_estimated for r in results)
    cost = compute_run_cost(avg_in_tokens, avg_out_tokens, provider)

    aggregated_metrics = MetricStats(
        total_workflow_steps=first.metrics.total_workflow_steps,
        openjev_calls=avg_openjev_calls,
        groq_calls=avg_groq_calls,
        tool_calls=avg_tool_calls,
        estimated_input_tokens=avg_in_tokens,
        estimated_output_tokens=avg_out_tokens,
        total_estimated_tokens=avg_total_tokens,
        latency_ms=avg_latency,
        min_latency_ms=min_lat,
        max_latency_ms=max_lat,
        fallback_occurred=fallback,
        is_estimated=is_est,
        token_source=token_src,
        cost_usd=cost
    )

    return AgentRunResult(
        task=first.task,
        jev_decision=first.jev_decision,
        execution_plan=first.execution_plan,
        trace=first.trace,
        tool_results=first.tool_results,
        final_answer=first.final_answer,
        metrics=aggregated_metrics
    )

def calculate_comparison_metrics(
    naive_result: AgentRunResult,
    jev_result: AgentRunResult,
    provider: Optional[str] = None,
    runs: int = 1
) -> ComparisonMetrics:
    n_m = naive_result.metrics
    j_m = jev_result.metrics
    p_key = (provider or "groq").lower()

    n_cost = compute_run_cost(n_m.estimated_input_tokens, n_m.estimated_output_tokens, p_key)
    j_cost = compute_run_cost(j_m.estimated_input_tokens, j_m.estimated_output_tokens, p_key)
    n_m.cost_usd = n_cost
    j_m.cost_usd = j_cost

    llm_avoided = round(n_m.groq_calls - j_m.groq_calls, 2)
    tool_avoided = round(n_m.tool_calls - j_m.tool_calls, 2)

    token_saved = n_m.total_estimated_tokens - j_m.total_estimated_tokens
    if n_m.total_estimated_tokens > 0:
        raw_token_pct = ((n_m.total_estimated_tokens - j_m.total_estimated_tokens) / float(n_m.total_estimated_tokens)) * 100.0
        token_reduction_pct = round(raw_token_pct, 2)
    else:
        token_reduction_pct = 0.0

    latency_diff_ms = round(n_m.latency_ms - j_m.latency_ms, 2)
    if n_m.latency_ms > 0:
        raw_lat_pct = ((n_m.latency_ms - j_m.latency_ms) / float(n_m.latency_ms)) * 100.0
        latency_change_pct = round(raw_lat_pct, 2)
    else:
        latency_change_pct = 0.0

    cost_saved_usd = round(n_cost - j_cost, 6)
    cost_saved_10k_usd = round(cost_saved_usd * 10000.0, 2)

    pricing_info = MODEL_PRICING.get(p_key, MODEL_PRICING["groq"])

    return ComparisonMetrics(
        runs=runs,
        llm_calls_avoided=llm_avoided,
        tool_calls_avoided=tool_avoided,
        token_saved=float(token_saved),
        token_reduction_percentage=token_reduction_pct,
        latency_diff_ms=latency_diff_ms,
        latency_change_percentage=latency_change_pct,
        naive_avg_latency_ms=n_m.latency_ms,
        naive_min_latency_ms=n_m.min_latency_ms or n_m.latency_ms,
        naive_max_latency_ms=n_m.max_latency_ms or n_m.latency_ms,
        jev_avg_latency_ms=j_m.latency_ms,
        jev_min_latency_ms=j_m.min_latency_ms or j_m.latency_ms,
        jev_max_latency_ms=j_m.max_latency_ms or j_m.latency_ms,
        estimated_cost_saved_usd=cost_saved_usd,
        estimated_cost_saved_10k_usd=cost_saved_10k_usd,
        pricing_model=pricing_info,
        provider=p_key,
        token_source=j_m.token_source
    )
