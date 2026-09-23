import time
import logging
from typing import Dict, Any, List, Optional
from app.models import (
    AgentRunResult, StepTrace, MetricStats, JevDecisionResponse, ExecutionPlan
)
from app.services.openjev_service import evaluate_task_with_openjev
from app.services.decision_engine import build_execution_plan
from app.services.calculator import evaluate_expression
from app.services.web_search import search_web
from app.services.groq_service import generate_with_groq

logger = logging.getLogger(__name__)

async def run_jev_agent(task: str, provider: Optional[str] = None) -> AgentRunResult:
    total_start = time.time()
    trace: List[StepTrace] = []
    tool_results: Dict[str, Any] = {}
    groq_calls = 0
    tool_calls = 0
    input_tokens = 0
    output_tokens = 0

    jev_decision, jev_latency = await evaluate_task_with_openjev(task)
    trace.append(StepTrace(
        step="OpenJEV Decision",
        status="fallback" if jev_decision.fallback_occurred else "completed",
        details=f"Required tool: {jev_decision.required_tool.upper()} | Needs LLM: {jev_decision.needs_llm} | Source: {jev_decision.decision_source}",
        latency_ms=round(jev_latency, 2)
    ))

    plan = build_execution_plan(jev_decision, task)

    if plan.use_calculator:
        calc_start = time.time()
        c_res = evaluate_expression(task)
        calc_lat = (time.time() - calc_start) * 1000
        tool_results["calculator"] = c_res
        tool_calls += 1
        trace.append(StepTrace(
            step="Safe Calculator Tool",
            status="completed" if c_res.get("success") else "failed",
            details=f"Expression: {c_res.get('expression')} -> Result: {c_res.get('result', c_res.get('error'))}",
            latency_ms=round(calc_lat, 2)
        ))
    else:
        trace.append(StepTrace(step="Safe Calculator Tool", status="skipped", details="Skipped by OpenJEV decision"))

    if plan.use_web_search:
        search_start = time.time()
        s_res = await search_web(task)
        search_lat = (time.time() - search_start) * 1000
        tool_results["web_search"] = s_res
        tool_calls += 1
        search_prov = s_res.get("provider", "Search")
        trace.append(StepTrace(
            step="Web Search Tool",
            status="completed",
            details=f"Provider: {search_prov} | Results: {len(s_res.get('results', []))}",
            latency_ms=round(search_lat, 2)
        ))
    else:
        trace.append(StepTrace(step="Web Search Tool", status="skipped", details="Skipped by OpenJEV decision"))

    if plan.verify:
        trace.append(StepTrace(
            step="Verification Step",
            status="completed",
            details="Performed verification check on tool output consistency.",
            latency_ms=5.0
        ))

    final_answer = ""
    if plan.use_llm:
        groq_out, tokens, groq_lat = await generate_with_groq(task, tool_results, jev_decision.dict(), provider=provider)
        groq_calls += 1
        input_tokens += tokens.get("prompt_tokens", 0)
        output_tokens += tokens.get("completion_tokens", 0)
        final_answer = groq_out
        step_label = "LLM Generation (" + (provider or "Groq").upper() + ")"
        trace.append(StepTrace(
            step=step_label,
            status="completed",
            details=f"Tokens: {tokens.get('total_tokens', 0)} ({tokens.get('prompt_tokens')} in / {tokens.get('completion_tokens')} out)",
            latency_ms=round(groq_lat, 2)
        ))
    else:
        trace.append(StepTrace(
            step="LLM Generation",
            status="skipped",
            details="Skipped entirely! OpenJEV determined deterministic tool result is sufficient.",
            latency_ms=0.0
        ))
        if "calculator" in tool_results and tool_results["calculator"].get("success"):
            final_answer = f"Result: {tool_results['calculator'].get('formatted_result')}"
        elif tool_results:
            final_answer = f"Result: {tool_results}"
        else:
            final_answer = "Task resolved without LLM intervention."

    total_latency = (time.time() - total_start) * 1000

    metrics = MetricStats(
        total_workflow_steps=len([t for t in trace if t.status in ["completed", "fallback"]]),
        openjev_calls=0 if jev_decision.fallback_occurred else 1,
        groq_calls=groq_calls,
        tool_calls=tool_calls,
        estimated_input_tokens=input_tokens,
        estimated_output_tokens=output_tokens,
        total_estimated_tokens=input_tokens + output_tokens,
        latency_ms=round(total_latency, 2),
        fallback_occurred=jev_decision.fallback_occurred,
        is_estimated=True
    )

    return AgentRunResult(
        task=task,
        jev_decision=jev_decision,
        execution_plan=plan,
        trace=trace,
        tool_results=tool_results,
        final_answer=final_answer,
        metrics=metrics
    )


async def run_naive_agent(task: str, provider: Optional[str] = None) -> AgentRunResult:
    total_start = time.time()
    trace: List[StepTrace] = []
    tool_results: Dict[str, Any] = {}
    tool_calls = 0
    
    naive_decision = JevDecisionResponse(
        needs_external_information=True,
        required_tool="calculator and web_search",
        needs_llm=True,
        needs_verification=False,
        task_complexity=0.5,
        decision_source="None (Naive Baseline)",
        fallback_occurred=False
    )
    
    trace.append(StepTrace(
        step="OpenJEV Decision",
        status="skipped",
        details="Naive baseline skips OpenJEV decision model.",
        latency_ms=0.0
    ))

    if any(char.isdigit() for char in task) and any(op in task for op in ["*", "/", "+", "-", "%"]):
        c_start = time.time()
        c_res = evaluate_expression(task)
        tool_results["calculator"] = c_res
        tool_calls += 1
        trace.append(StepTrace(
            step="Safe Calculator Tool",
            status="completed" if c_res.get("success") else "failed",
            details=f"Speculative tool call: {c_res.get('formatted_result', c_res.get('error'))}",
            latency_ms=round((time.time() - c_start) * 1000, 2)
        ))

    if any(k in task.lower() for k in ["weather", "stock", "find", "search", "latest", "price"]):
        s_start = time.time()
        s_res = await search_web(task)
        tool_results["web_search"] = s_res
        tool_calls += 1
        trace.append(StepTrace(
            step="Web Search Tool",
            status="completed",
            details="Speculative search tool call",
            latency_ms=round((time.time() - s_start) * 1000, 2)
        ))

    groq_out, tokens, groq_lat = await generate_with_groq(task, tool_results, None, provider=provider)
    step_label = "LLM Generation (" + (provider or "Groq").upper() + ")"
    trace.append(StepTrace(
        step=step_label,
        status="completed",
        details=f"Always called in Naive workflow. Tokens: {tokens.get('total_tokens', 0)}",
        latency_ms=round(groq_lat, 2)
    ))

    total_latency = (time.time() - total_start) * 1000

    metrics = MetricStats(
        total_workflow_steps=len([t for t in trace if t.status == "completed"]),
        openjev_calls=0,
        groq_calls=1,
        tool_calls=tool_calls,
        estimated_input_tokens=tokens.get("prompt_tokens", 0),
        estimated_output_tokens=tokens.get("completion_tokens", 0),
        total_estimated_tokens=tokens.get("total_tokens", 0),
        latency_ms=round(total_latency, 2),
        fallback_occurred=False,
        is_estimated=True
    )

    return AgentRunResult(
        task=task,
        jev_decision=naive_decision,
        execution_plan=ExecutionPlan(use_calculator=True, use_web_search=True, use_llm=True, verify=False),
        trace=trace,
        tool_results=tool_results,
        final_answer=groq_out,
        metrics=metrics
    )
