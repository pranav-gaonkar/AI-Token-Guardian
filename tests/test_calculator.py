import pytest
import sys
from pathlib import Path

# Add backend directory to sys.path so app imports work cleanly
backend_path = Path(__file__).resolve().parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.services.calculator import evaluate_expression

def test_basic_arithmetic():
    res = evaluate_expression("27 * 43")
    assert res["success"] is True
    assert res["result"] == 1161

def test_complex_expression():
    res = evaluate_expression("(10 + 5) * 4 / 2")
    assert res["success"] is True
    assert res["result"] == 30

def test_zero_division():
    res = evaluate_expression("50 / 0")
    assert res["success"] is False
    assert "ZeroDivisionError" in res["error"] or "zero" in res["error"].lower()

def test_prefix_stripping():
    res = evaluate_expression("Calculate 12345 * 67890?")
    assert res["success"] is True
    assert res["result"] == 838102050

def test_invalid_syntax():
    res = evaluate_expression("27 * * 43")
    assert res["success"] is False
    assert "Invalid mathematical syntax" in res["error"] or "SyntaxError" in res["error"]
