import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

backend_path = Path(__file__).resolve().parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "config" in data

def test_get_examples():
    response = client.get("/api/examples")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3

def test_run_agent_calculator():
    response = client.post("/api/run", json={"task": "Calculate 27 * 43."})
    assert response.status_code == 200
    data = response.json()
    assert "jev_decision" in data
    assert "execution_plan" in data
    assert "trace" in data
    assert "metrics" in data
    assert data["execution_plan"]["use_calculator"] is True

def test_compare_agent_endpoint():
    response = client.post("/api/compare", json={"task": "Calculate 100 * 50"})
    assert response.status_code == 200
    data = response.json()
    assert "baseline_naive" in data
    assert "optimized_jev" in data
    assert "comparison" in data
    assert "llm_calls_avoided" in data["comparison"]

def test_empty_task_validation():
    response = client.post("/api/run", json={"task": "   "})
    assert response.status_code == 400
