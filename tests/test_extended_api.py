import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

backend_path = Path(__file__).resolve().parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.main import app

client = TestClient(app)


class TestBenchmarkEndpoint:
    def test_benchmark_returns_all_categories(self):
        response = client.post("/api/benchmark", json={"task": "benchmark", "provider": "groq", "runs": 1})
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 5
        assert "provider" in data
        assert "runs_per_task" in data
        assert "pricing_model" in data
        assert data["runs_per_task"] >= 1

    def test_benchmark_results_structure(self):
        response = client.post("/api/benchmark", json={"task": "benchmark", "provider": "groq", "runs": 1})
        data = response.json()
        for result in data["results"]:
            assert "baseline_naive" in result
            assert "optimized_jev" in result
            assert "comparison" in result
            assert "task" in result
            assert result["baseline_naive"]["metrics"]["total_estimated_tokens"] >= 0
            assert result["optimized_jev"]["metrics"]["total_estimated_tokens"] >= 0

    def test_benchmark_comparison_metrics(self):
        response = client.post("/api/benchmark", json={"task": "benchmark", "provider": "groq", "runs": 1})
        data = response.json()
        for result in data["results"]:
            comp = result["comparison"]
            assert "llm_calls_avoided" in comp
            assert "tool_calls_avoided" in comp
            assert "token_reduction_percentage" in comp
            assert "latency_diff_ms" in comp
            assert "estimated_cost_saved_usd" in comp


class TestDecisionEndpoint:
    def test_decision_calculator(self):
        response = client.post("/api/decision", json={"task": "Calculate 100 * 50"})
        assert response.status_code == 200
        data = response.json()
        assert data["required_tool"] == "calculator"
        assert data["needs_llm"] is False

    def test_decision_web_search(self):
        response = client.post("/api/decision", json={"task": "What is the current weather in Berlin?"})
        assert response.status_code == 200
        data = response.json()
        assert data["required_tool"] == "web_search"
        assert data["needs_external_information"] is True

    def test_decision_llm_only(self):
        response = client.post("/api/decision", json={"task": "Explain how photosynthesis works"})
        assert response.status_code == 200
        data = response.json()
        assert data["needs_llm"] is True

    def test_decision_empty_task(self):
        response = client.post("/api/decision", json={"task": "   "})
        assert response.status_code == 400


class TestErrorScenarios:
    def test_run_invalid_json(self):
        response = client.post("/api/run", content="not json", headers={"Content-Type": "application/json"})
        assert response.status_code == 422

    def test_compare_empty_task(self):
        response = client.post("/api/compare", json={"task": "   "})
        assert response.status_code == 400

    def test_run_with_unknown_provider(self):
        response = client.post("/api/run", json={"task": "Calculate 5 + 5", "provider": "nonexistent_provider"})
        assert response.status_code == 200
        data = response.json()
        assert "final_answer" in data

    def test_compare_with_provider(self):
        response = client.post("/api/compare", json={"task": "Calculate 10 + 20", "provider": "frontier_sim", "runs": 1})
        assert response.status_code == 200
        data = response.json()
        assert data["provider"] == "frontier_sim"
        assert data["runs"] == 1

    def test_health_returns_config(self):
        response = client.get("/health")
        data = response.json()
        assert "config" in data
        assert "has_openjev_key" in data["config"]
        assert "has_groq_key" in data["config"]
        assert "has_openai_key" in data["config"]
        assert "llm_provider" in data["config"]

    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "documentation" in data
