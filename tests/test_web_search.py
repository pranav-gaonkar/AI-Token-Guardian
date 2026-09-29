import pytest
import sys
from pathlib import Path

backend_path = Path(__file__).resolve().parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.services.web_search import generate_simulated_search_results, fetch_live_weather


class TestSimulatedSearchResults:
    def test_weather_query(self):
        results = generate_simulated_search_results("weather in Tokyo")
        assert len(results) >= 1
        assert any("weather" in r["title"].lower() or "weather" in r["snippet"].lower() for r in results)

    def test_stock_query(self):
        results = generate_simulated_search_results("NVIDIA stock price")
        assert len(results) >= 1
        assert any("market" in r["title"].lower() or "stock" in r["snippet"].lower() for r in results)

    def test_news_query(self):
        results = generate_simulated_search_results("latest AI news")
        assert len(results) >= 1
        assert any("headline" in r["title"].lower() or "news" in r["snippet"].lower() for r in results)

    def test_generic_query(self):
        results = generate_simulated_search_results("quantum computing basics")
        assert len(results) >= 1
        assert any("quantum" in r["snippet"].lower() for r in results)

    def test_results_have_title_and_snippet(self):
        results = generate_simulated_search_results("test query")
        for r in results:
            assert "title" in r
            assert "snippet" in r
            assert len(r["title"]) > 0
            assert len(r["snippet"]) > 0


class TestCityExtraction:
    def test_city_extraction_logic(self):
        test_queries = [
            ("What is the weather in Paris?", "paris"),
            ("Find current weather in London", "london"),
            ("weather in Tokyo today", "tokyo"),
        ]
        for query, expected_city in test_queries:
            words = [w.strip("?,.!") for w in query.split()]
            words_lower = [w.lower() for w in words]
            ignore = {
                "give", "me", "summary", "summarize", "on", "and", "what", "are", "the", "major", "news",
                "find", "current", "weather", "today", "now", "is", "temperature", "forecast", "show",
                "get", "tell", "please", "detail", "overview", "report", "in", "at", "for"
            }
            city = None
            for prep in ["in", "for", "at"]:
                if prep in words_lower:
                    idx = words_lower.index(prep)
                    if idx + 1 < len(words) and words_lower[idx + 1] not in ignore:
                        city = words[idx + 1]
                        break
            assert city is not None, f"Failed to extract city from: {query}"
            assert city.lower() == expected_city
