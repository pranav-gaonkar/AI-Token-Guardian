import logging
import time
import asyncio
import httpx
from typing import Dict, Any, Tuple, Optional
from app.config import settings

logger = logging.getLogger(__name__)

async def generate_with_llm(
    user_request: str,
    tool_results: Optional[Dict[str, Any]] = None,
    jev_decisions: Optional[Dict[str, Any]] = None,
    provider: Optional[str] = None
) -> Tuple[str, Dict[str, int], float]:
    start_time = time.time()
    selected_provider = (provider or settings.LLM_PROVIDER).lower()
    
    system_prompt = (
        "You are the final response generator for an AI agent. "
        "Summarize the provided context and tool results into a clear, direct natural language answer for the user. "
        "Do NOT invoke any tools or format your output as JSON tool calls. "
        "If information is unavailable, state so concisely."
    )
    
    context_str = f"User Request: {user_request}\n"
    if tool_results:
        clean_tools = []
        if "calculator" in tool_results:
            c = tool_results["calculator"]
            if c.get("success"):
                clean_tools.append(f"Math Result: {c.get('formatted_result')}")
        if "web_search" in tool_results:
            s = tool_results["web_search"]
            res_list = s.get("results", [])
            snippets = " | ".join([r.get("snippet", "") for r in res_list[:2]])
            if snippets:
                clean_tools.append(f"Search Snippets: {snippets}")
        if clean_tools:
            context_str += "Context:\n" + "\n".join(clean_tools) + "\n"

    if selected_provider == "openai":
        if settings.has_openai_key:
            res = await _call_openai(system_prompt, context_str, start_time)
            if res:
                return res
            return f"OpenAI API call failed. Please check your OPENAI_API_KEY or network connection.", {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}, (time.time() - start_time) * 1000
        else:
            return "OpenAI provider selected, but OPENAI_API_KEY is not set in .env", {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}, (time.time() - start_time) * 1000

    elif selected_provider == "gemini":
        if settings.has_gemini_key:
            res, err_detail = await _call_gemini(system_prompt, context_str, start_time)
            if res:
                return res
            return f"Google Gemini API call failed.\nDetails: {err_detail}", {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}, (time.time() - start_time) * 1000
        else:
            return "Google Gemini provider selected, but GEMINI_API_KEY is not set in .env", {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}, (time.time() - start_time) * 1000

    elif selected_provider in ["groq", "frontier_sim"]:
        if settings.has_groq_key:
            res = await _call_groq(system_prompt, context_str, start_time, selected_provider == "frontier_sim")
            if res:
                return res
            return f"Groq API call failed. Please check your GROQ_API_KEY in .env.", {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}, (time.time() - start_time) * 1000

    if settings.has_gemini_key:
        res, _ = await _call_gemini(system_prompt, context_str, start_time)
        if res:
            return res

    if settings.has_groq_key:
        res = await _call_groq(system_prompt, context_str, start_time, False)
        if res:
            return res

    if settings.has_openai_key:
        res = await _call_openai(system_prompt, context_str, start_time)
        if res:
            return res

    mock_output = generate_mock_groq_response(user_request, tool_results)
    latency_ms = (time.time() - start_time) * 1000
    tokens = {
        "prompt_tokens": len(context_str.split()) * 2,
        "completion_tokens": len(mock_output.split()) * 2,
        "total_tokens": (len(context_str.split()) + len(mock_output.split())) * 2
    }
    return mock_output, tokens, latency_ms

generate_with_groq = generate_with_llm


async def _call_openai(system_prompt: str, context_str: str, start_time: float) -> Optional[Tuple[str, Dict[str, int], float]]:
    try:
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        body = {
            "model": settings.OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context_str}
            ],
            "temperature": 0.3,
            "max_tokens": 1000
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.post("https://api.openai.com/v1/chat/completions", json=body, headers=headers)
            latency_ms = (time.time() - start_time) * 1000
            if res.status_code == 200:
                data = res.json()
                output_text = data["choices"][0]["message"]["content"] or ""
                usage = data.get("usage", {})
                tokens = {
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0)
                }
                return output_text, tokens, latency_ms
            else:
                logger.warning(f"OpenAI API HTTP {res.status_code}: {res.text}")
    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
    return None


async def _call_gemini(system_prompt: str, context_str: str, start_time: float) -> Tuple[Optional[Tuple[str, Dict[str, int], float]], Optional[str]]:
    candidate_models = [
        settings.GEMINI_MODEL,
        "gemini-3.5-flash-lite",
        "gemini-3.5-flash",
        "gemini-3.1-pro-preview"
    ]
    models_to_try = []
    for m in candidate_models:
        if m and m not in models_to_try:
            models_to_try.append(m)

    last_error = ""
    for model_name in models_to_try:
        try:
            gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={settings.GEMINI_API_KEY}"
            body = {
                "contents": [{
                    "parts": [{"text": f"{system_prompt}\n\n{context_str}"}]
                }]
            }
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(gemini_url, json=body)
                latency_ms = (time.time() - start_time) * 1000
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        output_text = parts[0].get("text", "") if parts else ""
                        meta = data.get("usageMetadata", {})
                        tokens = {
                            "prompt_tokens": meta.get("promptTokenCount", 0),
                            "completion_tokens": meta.get("candidatesTokenCount", 0),
                            "total_tokens": meta.get("totalTokenCount", 0)
                        }
                        logger.info(f"Successfully called Gemini model: {model_name}")
                        return (output_text, tokens, latency_ms), None
                else:
                    last_error = f"Model '{model_name}' HTTP {res.status_code}: {res.text[:200]}"
                    logger.warning(f"Gemini API ({model_name}) HTTP {res.status_code}: {res.text}")
        except Exception as e:
            last_error = f"Model '{model_name}' exception: {str(e)}"
            logger.error(f"Gemini API ({model_name}) error: {str(e)}")

    logger.error(f"All Gemini models failed. Last error: {last_error}")
    return None, last_error


async def _call_groq(system_prompt: str, context_str: str, start_time: float, is_simulated: bool = False) -> Optional[Tuple[str, Dict[str, int], float]]:
    try:
        from groq import AsyncGroq
        client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        
        response = await client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context_str}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        latency_ms = (time.time() - start_time) * 1000

        if is_simulated:
            await asyncio.sleep(0.5)
            latency_ms += 1500.0

        output_text = response.choices[0].message.content or ""
        
        usage = response.usage
        tokens = {
            "prompt_tokens": getattr(usage, "prompt_tokens", 0) if usage else 0,
            "completion_tokens": getattr(usage, "completion_tokens", 0) if usage else 0,
            "total_tokens": getattr(usage, "total_tokens", 0) if usage else 0
        }
        
        return output_text, tokens, latency_ms

    except Exception as e:
        logger.error(f"Groq API error: {str(e)}")
    return None


def generate_mock_groq_response(task: str, tool_results: Optional[Dict[str, Any]]) -> str:
    if tool_results and "calculator" in tool_results:
        calc_res = tool_results["calculator"]
        if calc_res.get("success"):
            return f"The calculated answer is {calc_res.get('result')}. ({calc_res.get('formatted_result')})"
        else:
            return f"Calculation error: {calc_res.get('error')}"

    if tool_results and "web_search" in tool_results:
        search_res = tool_results["web_search"]
        results = search_res.get("results", [])
        snippets = "\n".join([f"- {r['title']}: {r['snippet']}" for r in results[:2]])
        return f"Based on web search results for '{task}':\n\n{snippets}\n\n[Note: Add GROQ_API_KEY to .env to enable real Groq LLM generations.]"

    return (
        f"Response to: '{task}'\n\n"
        "This query was processed by AI Token Guardian. "
        "To get live AI responses from Groq, please populate GROQ_API_KEY in your root .env file."
    )

