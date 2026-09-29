import pytest
import sys
from pathlib import Path

backend_path = Path(__file__).resolve().parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.services.metrics import compute_run_cost, aggregate_agent_results, calculate_comparison_metrics
from app.models import AgentRunResult, MetricStats, JevDecisionResponse, ExecutionPlan, StepTrace


def _make_run_result(
    groq_calls=1.0, tool_calls=1.0,
    input_tokens=100, output_tokens=50,
    latency_ms=500.0, task="test task"
):
    return AgentRunResult(
        task=task,
        jev_decision=JevDecisionResponse(
            needs_external_information=False,
            required_tool="none",
            needs_llm=True,
            needs_verification=False,
            task_complexity=0.5
        ),
        execution_plan=ExecutionPlan(use_calculator=False, use_web_search=False, use_llm=True, verify=False),
        trace=[StepTrace(step="Test Step", status="completed", latency_ms=latency_ms)],
        tool_results={},
        final_answer="test",
        metrics=MetricStats(
            total_workflow_steps=1,
            openjev_calls=1.0,
            groq_calls=groq_calls,
            tool_calls=tool_calls,
            estimated_input_tokens=input_tokens,
            estimated_output_tokens=output_tokens,
            total_estimated_tokens=input_tokens + output_tokens,
            latency_ms=latency_ms,
            min_latency_ms=latency_ms,
            max_latency_ms=latency_ms,
            fallback_occurred=False,
            is_estimated=True,
            token_source="estimated"
        )
    )


class TestComputeRunCost:
    def test_groq_pricing(self):
        cost = compute_run_cost(1000, 1000, "groq")
        expected = (1000 / 1000 * 0.0001) + (1000 / 1000 * 0.0002)
        assert cost == round(expected, 6)

    def test_openai_pricing(self):
        cost = compute_run_cost(1000, 1000, "openai")
        expected = (1000 / 1000 * 0.00015) + (1000 / 1000 * 0.0006)
        assert cost == round(expected, 6)

    def test_gemini_pricing(self):
        cost = compute_run_cost(1000, 1000, "gemini")
        expected = (1000 / 1000 * 0.000075) + (1000 / 1000 * 0.0003)
        assert cost == round(expected, 6)

    def test_frontier_sim_pricing(self):
        cost = compute_run_cost(1000, 1000, "frontier_sim")
        expected = (1000 / 1000 * 0.0025) + (1000 / 1000 * 0.010)
        assert cost == round(expected, 6)

    def test_zero_tokens(self):
        cost = compute_run_cost(0, 0, "groq")
        assert cost == 0.0

    def test_unknown_provider_defaults_to_groq(self):
        cost = compute_run_cost(1000, 1000, "unknown_provider")
        groq_cost = compute_run_cost(1000, 1000, "groq")
        assert cost == groq_cost

    def test_none_provider_defaults_to_groq(self):
        cost = compute_run_cost(500, 200)
        groq_cost = compute_run_cost(500, 200, "groq")
        assert cost == groq_cost


class TestAggregateAgentResults:
    def test_single_result(self):
        r = _make_run_result(input_tokens=100, output_tokens=50)
        agg = aggregate_agent_results([r], provider="groq")
        assert agg.metrics.estimated_input_tokens == 100
        assert agg.metrics.estimated_output_tokens == 50
        assert agg.metrics.cost_usd > 0

    def test_multiple_results_averaging(self):
        r1 = _make_run_result(input_tokens=100, output_tokens=50, latency_ms=400.0)
        r2 = _make_run_result(input_tokens=200, output_tokens=100, latency_ms=600.0)
        agg = aggregate_agent_results([r1, r2], provider="groq")
        assert agg.metrics.estimated_input_tokens == 150
        assert agg.metrics.estimated_output_tokens == 75
        assert agg.metrics.latency_ms == 500.0
        assert agg.metrics.min_latency_ms == 400.0
        assert agg.metrics.max_latency_ms == 600.0

    def test_empty_list_raises(self):
        with pytest.raises(ValueError, match="Cannot aggregate empty"):
            aggregate_agent_results([])


class TestCalculateComparisonMetrics:
    def test_full_savings(self):
        naive = _make_run_result(groq_calls=1.0, tool_calls=2.0, input_tokens=200, output_tokens=100, latency_ms=1000.0)
        jev = _make_run_result(groq_calls=0.0, tool_calls=1.0, input_tokens=0, output_tokens=0, latency_ms=5.0)
        comp = calculate_comparison_metrics(naive, jev, provider="groq", runs=1)
        assert comp.llm_calls_avoided == 1.0
        assert comp.tool_calls_avoided == 1.0
        assert comp.token_reduction_percentage == 100.0
        assert comp.token_saved == 300.0
        assert comp.latency_diff_ms > 0
        assert comp.estimated_cost_saved_usd > 0
        assert comp.estimated_cost_saved_10k_usd > 0

    def test_no_savings(self):
        naive = _make_run_result(groq_calls=1.0, tool_calls=1.0, input_tokens=100, output_tokens=50, latency_ms=500.0)
        jev = _make_run_result(groq_calls=1.0, tool_calls=1.0, input_tokens=100, output_tokens=50, latency_ms=500.0)
        comp = calculate_comparison_metrics(naive, jev, provider="groq", runs=1)
        assert comp.llm_calls_avoided == 0.0
        assert comp.tool_calls_avoided == 0.0
        assert comp.token_reduction_percentage == 0.0
        assert comp.token_saved == 0.0
        assert comp.latency_diff_ms == 0.0

    def test_provider_propagation(self):
        naive = _make_run_result()
        jev = _make_run_result()
        comp = calculate_comparison_metrics(naive, jev, provider="openai", runs=3)
        assert comp.provider == "openai"
        assert comp.runs == 3
        assert "input_price_per_1k" in comp.pricing_model
