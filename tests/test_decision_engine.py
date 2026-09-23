import pytest
import sys
from pathlib import Path

backend_path = Path(__file__).resolve().parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.models import JevDecisionResponse
from app.services.openjev_service import parse_openjev_response, apply_fallback_rules
from app.services.decision_engine import build_execution_plan

def test_parse_openjev_structured_response():
    sample_res = {
        "answers": {
            "needs_external_information": {"answer": "no"},
            "required_tool": {"answer": "calculator"},
            "needs_llm": {"answer": "no"},
            "needs_verification": {"answer": "no"},
            "task_complexity": {"answer": 0.2}
        }
    }
    decision = parse_openjev_response(sample_res)
    assert decision.needs_external_information is False
    assert decision.required_tool == "calculator"
    assert decision.needs_llm is False
    assert decision.task_complexity == 0.2
    assert decision.fallback_occurred is False

def test_decision_engine_calculator_plan():
    decision = JevDecisionResponse(
        needs_external_information=False,
        required_tool="calculator",
        needs_llm=False,
        needs_verification=False,
        task_complexity=0.1
    )
    plan = build_execution_plan(decision, "Calculate 27 * 43")
    assert plan.use_calculator is True
    assert plan.use_web_search is False
    assert plan.use_llm is False

def test_decision_engine_contradiction_override():
    # If no tool is required AND needs_llm is set to False (contradictory dead-end),
    # decision engine should override needs_llm to True.
    decision = JevDecisionResponse(
        needs_external_information=False,
        required_tool="none",
        needs_llm=False,
        needs_verification=False,
        task_complexity=0.5
    )
    plan = build_execution_plan(decision, "Explain quantum computing")
    assert plan.use_llm is True

def test_fallback_rules_math():
    decision = apply_fallback_rules("Calculate 100 / 5", reason="Missing API key")
    assert decision.required_tool == "calculator"
    assert decision.fallback_occurred is True
    assert "Missing API key" in decision.fallback_reason

def test_fallback_rules_search():
    decision = apply_fallback_rules("What is the current weather in Paris?", reason="Timeout")
    assert decision.required_tool == "web_search"
    assert decision.needs_external_information is True
    assert decision.fallback_occurred is True
