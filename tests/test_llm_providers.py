import pytest
import sys
import asyncio
from pathlib import Path
from unittest.mock import patch

backend_path = Path(__file__).resolve().parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.services.groq_service import generate_with_llm, generate_mock_groq_response


class TestMockGroqResponse:
    def test_calculator_success(self):
        tool_results = {
            "calculator": {"success": True, "result": 1161, "formatted_result": "27 * 43 = 1161"}
        }
        response = generate_mock_groq_response("Calculate 27 * 43", tool_results)
        assert "1161" in response

    def test_calculator_error(self):
        tool_results = {
            "calculator": {"success": False, "error": "Division by zero"}
        }
        response = generate_mock_groq_response("Calculate 1/0", tool_results)
        assert "Division by zero" in response

    def test_search_results(self):
        tool_results = {
            "web_search": {
                "results": [
                    {"title": "Weather Tokyo", "snippet": "25°C, sunny"},
                    {"title": "Forecast", "snippet": "Clear skies"}
                ]
            }
        }
        response = generate_mock_groq_response("Weather in Tokyo", tool_results)
        assert "25°C" in response or "Weather Tokyo" in response

    def test_no_tools_fallback(self):
        response = generate_mock_groq_response("Tell me about AI", None)
        assert "AI Token Guardian" in response

    def test_empty_tools(self):
        response = generate_mock_groq_response("Hello", {})
        assert len(response) > 0


class TestLLMProviderFallback:
    def test_no_keys_uses_mock(self):
        with patch("app.services.groq_service.settings") as mock_settings:
            mock_settings.LLM_PROVIDER = "groq"
            mock_settings.has_groq_key = False
            mock_settings.has_gemini_key = False
            mock_settings.has_openai_key = False

            result, tokens, latency = asyncio.get_event_loop().run_until_complete(
                generate_with_llm(
                    "Explain TCP vs UDP",
                    tool_results=None,
                    jev_decisions=None,
                    provider="groq"
                )
            )
            assert isinstance(result, str)
            assert len(result) > 0
            assert tokens["is_estimated"] is True
            assert tokens["token_source"] == "estimated"

    def test_openai_without_key_returns_message(self):
        with patch("app.services.groq_service.settings") as mock_settings:
            mock_settings.LLM_PROVIDER = "openai"
            mock_settings.has_openai_key = False
            mock_settings.has_groq_key = False
            mock_settings.has_gemini_key = False

            result, tokens, latency = asyncio.get_event_loop().run_until_complete(
                generate_with_llm("Test", provider="openai")
            )
            assert "OPENAI_API_KEY" in result or "not set" in result.lower()

    def test_gemini_without_key_returns_message(self):
        with patch("app.services.groq_service.settings") as mock_settings:
            mock_settings.LLM_PROVIDER = "gemini"
            mock_settings.has_gemini_key = False
            mock_settings.has_groq_key = False
            mock_settings.has_openai_key = False

            result, tokens, latency = asyncio.get_event_loop().run_until_complete(
                generate_with_llm("Test", provider="gemini")
            )
            assert "GEMINI_API_KEY" in result or "not set" in result.lower()

    def test_context_formatting_with_tools(self):
        with patch("app.services.groq_service.settings") as mock_settings:
            mock_settings.LLM_PROVIDER = "groq"
            mock_settings.has_groq_key = False
            mock_settings.has_gemini_key = False
            mock_settings.has_openai_key = False

            tool_results = {
                "calculator": {"success": True, "formatted_result": "10 + 20 = 30"},
                "web_search": {"results": [{"title": "Test", "snippet": "Result text"}]}
            }

            result, tokens, latency = asyncio.get_event_loop().run_until_complete(
                generate_with_llm(
                    "Calculate 10 + 20",
                    tool_results=tool_results,
                    provider="groq"
                )
            )
            assert isinstance(result, str)
            assert tokens["total_tokens"] > 0
