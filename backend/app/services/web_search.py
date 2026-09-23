import httpx
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

async def search_web(query: str) -> Dict[str, Any]:
    cleaned_query = query.strip()
    
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(
                "https://api.duckduckgo.com/",
                params={"q": cleaned_query, "format": "json", "no_html": "1"}
            )
            if resp.status_code == 200:
                data = resp.json()
                abstract = data.get("AbstractText", "")
                heading = data.get("Heading", "")
                related = [t.get("Text") for t in data.get("RelatedTopics", []) if "Text" in t]
                
                if abstract or heading or related:
                    results = []
                    if abstract:
                        results.append({"title": heading or cleaned_query, "snippet": abstract})
                    for rel in related[:3]:
                        results.append({"title": "Related Result", "snippet": rel})
                        
                    return {
                        "query": cleaned_query,
                        "is_simulated": False,
                        "provider": "DuckDuckGo API",
                        "results": results
                    }
    except Exception as e:
        logger.warning(f"Live web search attempt failed: {str(e)}. Falling back to demo web search tool.")

    simulated_snippets = generate_simulated_search_results(cleaned_query)
    return {
        "query": cleaned_query,
        "is_simulated": True,
        "provider": "Demo search result",
        "notice": "Demo search result — No live paid API required",
        "results": simulated_snippets
    }

def generate_simulated_search_results(query: str) -> List[Dict[str, str]]:
    q_lower = query.lower()
    if "weather" in q_lower:
        return [
            {
                "title": f"Live Weather Data for {query}",
                "snippet": "Current Weather: 26°C, Partly Cloudy. Humidity: 65%. Wind: 12 km/h SW. High: 29°C, Low: 21°C."
            },
            {
                "title": "Weather Forecast & Climate Highlights",
                "snippet": "Expect clear skies towards the evening with light breezes. Air quality index (AQI): 58 (Moderate)."
            }
        ]
    elif "stock" in q_lower or "price" in q_lower or "nvidia" in q_lower:
        return [
            {
                "title": f"Market Overview: {query}",
                "snippet": f"Latest Market Update for {query}: Traded at $128.50 (+2.4% today). Volume: 42.1M. Market Cap: $3.15T."
            },
            {
                "title": "Financial News & Analysis",
                "snippet": "Strong quarterly performance driven by high AI infrastructure demand and enterprise datacenter growth."
            }
        ]
    elif "news" in q_lower or "latest" in q_lower:
        return [
            {
                "title": f"Top Headlines on {query}",
                "snippet": "Global technological updates highlight major breakthroughs in autonomous reasoning, efficient compute scaling, and AI tokens."
            }
        ]
    else:
        return [
            {
                "title": f"Web Search Result: {query}",
                "snippet": f"Information regarding '{query}': Key documentation, technical background, and related domain index data."
            },
            {
                "title": f"Community & Reference Notes: {query}",
                "snippet": f"Overview of topics associated with '{query}' summarizing public knowledge and references."
            }
        ]
