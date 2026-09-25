import httpx
import logging
import time
from typing import Dict, Any, Tuple, Optional
from app.config import settings
from app.models import JevDecisionResponse
from app.prompts.decision_questions import build_openjev_payload

logger = logging.getLogger(__name__)

_http_client: Optional[httpx.AsyncClient] = None

def get_fastpath_decision(task: str) -> Optional[JevDecisionResponse]:
    t_lower = task.lower().strip()
    
    math_words = [
        "calculate", "multiply", "multiplied", "times", "divide", "divided",
        "plus", "minus", "sum", "add", "added", "subtract", "subtracted",
        "product", "difference", "quotient", "what is", "sqrt", "power"
    ]
    has_digits = any(char.isdigit() for char in task)
    has_operators = any(op in task for op in ["*", "/", "+", "%"])
    is_calc = (any(w in t_lower for w in math_words) and has_digits) or (has_digits and has_operators)
    
    search_words = ["weather", "current", "stock", "price", "latest", "today", "news"]
    is_search = any(w in t_lower for w in search_words)

    has_explanation = any(w in t_lower for w in ["explain", "why", "how does", "describe", "detail"])

    if is_calc and not is_search:
        needs_llm = has_explanation or len(t_lower) > 60
        return JevDecisionResponse(
            needs_external_information=False,
            required_tool="calculator",
            needs_llm=needs_llm,
            needs_verification=False,
            task_complexity=0.2 if not needs_llm else 0.5,
            raw_answers={"fastpath": True, "required_tool": "calculator", "needs_llm": needs_llm},
            decision_source="OpenJEV Fast-Path",
            fallback_occurred=False
        )

    if is_search and not is_calc:
        needs_llm = has_explanation or ("summarize" in t_lower or "analyze" in t_lower)
        return JevDecisionResponse(
            needs_external_information=True,
            required_tool="web_search",
            needs_llm=needs_llm,
            needs_verification=False,
            task_complexity=0.3 if not needs_llm else 0.6,
            raw_answers={"fastpath": True, "required_tool": "web_search", "needs_llm": needs_llm},
            decision_source="OpenJEV Fast-Path",
            fallback_occurred=False
        )

    if not is_calc and not is_search and has_explanation:
        return JevDecisionResponse(
            needs_external_information=False,
            required_tool="none",
            needs_llm=True,
            needs_verification=False,
            task_complexity=0.4,
            raw_answers={"fastpath": True, "required_tool": "none", "needs_llm": True},
            decision_source="OpenJEV Fast-Path",
            fallback_occurred=False
        )

    return None

async def evaluate_task_with_openjev(task: str) -> Tuple[JevDecisionResponse, float]:
    start_time = time.time()

    fast_decision = get_fastpath_decision(task)
    if fast_decision:
        latency_ms = (time.time() - start_time) * 1000
        return fast_decision, max(0.5, round(latency_ms, 2))

    if not settings.has_openjev_key:
        logger.info("OPENJEV_API_KEY is not configured. Utilizing local heuristic fallback decision rules.")
        decision = apply_fallback_rules(
            task,
            reason="OPENJEV_API_KEY is missing from environment."
        )
        latency_ms = (time.time() - start_time) * 1000
        return decision, latency_ms

    payload = build_openjev_payload(task)
    headers = {
        "Authorization": f"Bearer {settings.OPENJEV_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            logger.info(f"Posting decision request to OpenJEV API: {settings.OPENJEV_URL}")
            response = await client.post(
                settings.OPENJEV_URL,
                json=payload,
                headers=headers
            )
            
            latency_ms = (time.time() - start_time) * 1000

        if response.status_code == 200:
            res_json = response.json()
            logger.info("OpenJEV API response successfully received.")
            decision = parse_openjev_response(res_json)
            return decision, latency_ms
        else:
            logger.warning(f"OpenJEV API returned HTTP {response.status_code}: {response.text}")
            decision = apply_fallback_rules(
                task,
                reason=f"OpenJEV API HTTP error status {response.status_code}."
            )
            return decision, latency_ms

    except httpx.TimeoutException:
        logger.error("OpenJEV API request timed out.")
        latency_ms = (time.time() - start_time) * 1000
        return apply_fallback_rules(task, reason="OpenJEV API request timeout."), latency_ms
    except Exception as e:
        logger.error(f"OpenJEV API request exception: {str(e)}")
        latency_ms = (time.time() - start_time) * 1000
        return apply_fallback_rules(task, reason=f"OpenJEV API connection error: {str(e)}"), latency_ms


def parse_openjev_response(response_json: Dict[str, Any]) -> JevDecisionResponse:
    answers = response_json.get("answers", response_json.get("questions", response_json.get("data", response_json)))
    
    def extract_val(q_id: str, default: Any) -> Any:
        q_obj = answers.get(q_id, {})
        if isinstance(q_obj, dict):
            if "choice" in q_obj and q_obj["choice"] is not None:
                return q_obj["choice"]
            if "noul" in q_obj and q_obj["noul"] is not None:
                return q_obj["noul"]
            if "score" in q_obj and q_obj["score"] is not None:
                return q_obj["score"]
            return q_obj.get("answer", q_obj.get("value", default))
        return q_obj if q_obj is not None else default

    def to_bool(val: Any, default: bool = False) -> bool:
        if isinstance(val, bool):
            return val
        if isinstance(val, (int, float)):
            return val >= 0.5
        if isinstance(val, str):
            clean = val.lower().strip()
            if clean in ["yes", "true", "1", "y"]:
                return True
            if clean in ["no", "false", "0", "n"]:
                return False
            try:
                return float(clean) >= 0.5
            except ValueError:
                pass
        return default

    raw_ext_info = extract_val("needs_external_information", False)
    raw_tool = extract_val("required_tool", "none")
    raw_llm = extract_val("needs_llm", True)
    raw_verify = extract_val("needs_verification", False)
    raw_complexity = extract_val("task_complexity", 0.5)

    tool_clean = str(raw_tool).lower().strip()
    if tool_clean not in ["none", "calculator", "web_search"]:
        if "calc" in tool_clean:
            tool_clean = "calculator"
        elif "search" in tool_clean or "web" in tool_clean:
            tool_clean = "web_search"
        else:
            tool_clean = "none"

    try:
        complexity = float(raw_complexity)
        complexity = max(0.0, min(1.0, complexity))
    except (ValueError, TypeError):
        complexity = 0.5

    return JevDecisionResponse(
        needs_external_information=to_bool(raw_ext_info, False),
        required_tool=tool_clean,
        needs_llm=to_bool(raw_llm, True),
        needs_verification=to_bool(raw_verify, False),
        task_complexity=complexity,
        raw_answers=answers if isinstance(answers, dict) else {"raw": answers},
        decision_source="OpenJEV",
        fallback_occurred=False,
        fallback_reason=None
    )


def apply_fallback_rules(task: str, reason: str) -> JevDecisionResponse:
    t_lower = task.lower().strip()
    
    math_words = [
        "calculate", "+", "*", "/", "-", "%", "sum", "multiply", "multiplied", "times",
        "divide", "divided", "minus", "plus", "math", "add", "added", "subtract",
        "subtracted", "product", "difference", "quotient", "sqrt", "power"
    ]
    has_digits = any(char.isdigit() for char in task)
    is_calc = (any(w in t_lower for w in math_words) and has_digits) or (has_digits and any(op in task for op in ["*", "/", "+", "%"]))

    search_words = ["weather", "current", "stock", "price", "latest", "find", "search", "today", "news"]
    is_search = any(w in t_lower for w in search_words)
    has_explanation = any(w in t_lower for w in ["explain", "why", "how does", "describe", "detail"])

    if is_calc and not is_search:
        required_tool = "calculator"
        needs_llm = False if len(t_lower) < 30 and not has_explanation else True
        needs_ext = False
    elif is_search:
        required_tool = "web_search"
        needs_llm = has_explanation or ("summarize" in t_lower or "analyze" in t_lower)
        needs_ext = True
    else:
        required_tool = "none"
        needs_llm = True
        needs_ext = False

    return JevDecisionResponse(
        needs_external_information=needs_ext,
        required_tool=required_tool,
        needs_llm=needs_llm,
        needs_verification=False,
        task_complexity=0.3 if is_calc else 0.7,
        raw_answers={"fallback_rule": True},
        decision_source="Fallback Rules (OpenJEV unavailable)",
        fallback_occurred=True,
        fallback_reason=reason
    )
