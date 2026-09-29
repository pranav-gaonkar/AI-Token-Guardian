import pytest
import sys
from pathlib import Path

backend_path = Path(__file__).resolve().parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.services.openjev_service import get_fastpath_decision


def test_fastpath_pure_math():
    decision = get_fastpath_decision("Calculate 27 * 43")
    assert decision is not None
    assert decision.required_tool == "calculator"
    assert decision.needs_llm is False
    assert decision.needs_external_information is False
    assert decision.decision_source == "OpenJEV Fast-Path"
    assert decision.task_complexity == 0.2


def test_fastpath_math_with_operators():
    decision = get_fastpath_decision("100 + 200 * 3")
    assert decision is not None
    assert decision.required_tool == "calculator"
    assert decision.needs_llm is False


def test_fastpath_math_with_explanation():
    decision = get_fastpath_decision("Calculate 12345 * 67890 and explain the result in detail")
    assert decision is not None
    assert decision.required_tool == "calculator"
    assert decision.needs_llm is True
    assert decision.task_complexity == 0.5


def test_fastpath_weather_search():
    decision = get_fastpath_decision("What is the current weather in Tokyo?")
    assert decision is not None
    assert decision.required_tool == "web_search"
    assert decision.needs_external_information is True
    assert decision.decision_source == "OpenJEV Fast-Path"


def test_fastpath_stock_search():
    decision = get_fastpath_decision("latest stock price of NVIDIA")
    assert decision is not None
    assert decision.required_tool == "web_search"
    assert decision.needs_external_information is True


def test_fastpath_search_with_explanation():
    decision = get_fastpath_decision("Find the current weather in Paris and explain the climate patterns")
    assert decision is not None
    assert decision.required_tool == "web_search"
    assert decision.needs_llm is True


def test_fastpath_pure_llm_explanation():
    decision = get_fastpath_decision("Explain quantum computing")
    assert decision is not None
    assert decision.required_tool == "none"
    assert decision.needs_llm is True
    assert decision.needs_external_information is False


def test_fastpath_pure_llm_write():
    decision = get_fastpath_decision("Write a summary of machine learning")
    assert decision is not None
    assert decision.required_tool == "none"
    assert decision.needs_llm is True


def test_fastpath_no_match_returns_none():
    decision = get_fastpath_decision("hello")
    assert decision is None


def test_fastpath_ambiguous_returns_none():
    decision = get_fastpath_decision("Tell me something interesting")
    assert decision is None


def test_fastpath_math_nlp_multiplied():
    decision = get_fastpath_decision("25 multiplied by 4")
    assert decision is not None
    assert decision.required_tool == "calculator"
    assert decision.needs_llm is False


def test_fastpath_math_nlp_divide():
    decision = get_fastpath_decision("divide 100 by 5")
    assert decision is not None
    assert decision.required_tool == "calculator"


def test_fastpath_fallback_occurred_is_false():
    decision = get_fastpath_decision("Calculate 10 + 20")
    assert decision is not None
    assert decision.fallback_occurred is False
    assert decision.fallback_reason is None
