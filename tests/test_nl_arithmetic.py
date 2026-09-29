import pytest
import sys
from pathlib import Path

backend_path = Path(__file__).resolve().parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.services.calculator import extract_and_clean_math, evaluate_expression, solve_simple_equation


class TestExtractAndCleanMath:
    def test_multiplied_by(self):
        result = extract_and_clean_math("25 multiplied by 4")
        assert "*" in result
        assert "multiplied" not in result.lower()

    def test_times(self):
        result = extract_and_clean_math("10 times 5")
        assert "*" in result

    def test_divided_by(self):
        result = extract_and_clean_math("100 divided by 5")
        assert "/" in result

    def test_plus(self):
        result = extract_and_clean_math("50 plus 30")
        assert "+" in result

    def test_minus(self):
        result = extract_and_clean_math("100 minus 40")
        assert "-" in result

    def test_prefix_calculate(self):
        result = extract_and_clean_math("Calculate 27 * 43")
        assert "calculate" not in result.lower()
        assert "27" in result
        assert "43" in result

    def test_prefix_what_is(self):
        result = extract_and_clean_math("what is 10 + 20")
        assert "what is" not in result.lower()

    def test_percentage_of(self):
        result = extract_and_clean_math("15% of 200")
        assert "100" in result
        assert "15" in result
        assert "200" in result

    def test_trailing_question_mark(self):
        result = extract_and_clean_math("100 * 5?")
        assert "?" not in result

    def test_dollar_sign_stripped(self):
        result = extract_and_clean_math("$100 + $200")
        assert "$" not in result

    def test_stop_keyword_and(self):
        result = extract_and_clean_math("100 * 5 and explain the result")
        assert "explain" not in result.lower()

    def test_raw_arithmetic(self):
        result = extract_and_clean_math("(10 + 5) * 4")
        assert "10" in result
        assert "5" in result
        assert "4" in result


class TestSolveSimpleEquation:
    def test_simple_linear(self):
        result = solve_simple_equation("2x + 3 = 11")
        assert result is not None
        assert result["success"] is True
        assert result["result"] == 4

    def test_no_equation(self):
        result = solve_simple_equation("hello world")
        assert result is None

    def test_negative_coefficient(self):
        result = solve_simple_equation("-3x + 9 = 0")
        assert result is not None
        assert result["success"] is True
        assert result["result"] == 3


class TestEvaluateExpressionNLP:
    def test_nl_multiply(self):
        res = evaluate_expression("25 multiplied by 4")
        assert res["success"] is True
        assert res["result"] == 100

    def test_nl_times(self):
        res = evaluate_expression("7 times 8")
        assert res["success"] is True
        assert res["result"] == 56

    def test_nl_divided_by(self):
        res = evaluate_expression("100 divided by 4")
        assert res["success"] is True
        assert res["result"] == 25

    def test_nl_plus(self):
        res = evaluate_expression("50 plus 30")
        assert res["success"] is True
        assert res["result"] == 80

    def test_percentage(self):
        res = evaluate_expression("20% of 500")
        assert res["success"] is True
        assert res["result"] == 100

    def test_equation_solver(self):
        res = evaluate_expression("solve for x in 5x + 10 = 35")
        assert res["success"] is True
        assert res["result"] == 5

    def test_float_result(self):
        res = evaluate_expression("10 / 3")
        assert res["success"] is True
        assert isinstance(res["result"], float)
        assert abs(res["result"] - 3.333333) < 0.001

    def test_nested_parentheses(self):
        res = evaluate_expression("((2 + 3) * (4 + 1))")
        assert res["success"] is True
        assert res["result"] == 25

    def test_power(self):
        res = evaluate_expression("2 ** 10")
        assert res["success"] is True
        assert res["result"] == 1024

    def test_modulo(self):
        res = evaluate_expression("17 % 5")
        assert res["success"] is True
        assert isinstance(res["result"], (int, float))
