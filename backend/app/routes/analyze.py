import asyncio
from datetime import datetime
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.models import (
    TaskRequest, AgentRunResult, ComparisonResult, JevDecisionResponse, ExampleTask, BenchmarkSuiteResult
)
from app.services.agent_runner import run_jev_agent, run_naive_agent
from app.services.openjev_service import evaluate_task_with_openjev
from app.services.metrics import calculate_comparison_metrics, aggregate_agent_results, MODEL_PRICING

router = APIRouter(prefix="/api", tags=["Agent Analysis"])

PREDEFINED_EXAMPLES: List[ExampleTask] = [
    ExampleTask(
        id="ex1",
        title="1. Category A: Pure Calculation",
        category="Category A: Basic / Simple Tasks",
        task="Calculate 27 * 43.",
        expected_tool="Calculator (LLM avoided)",
        description="Deterministic math. OpenJEV routes to AST calculator, bypassing LLM (100% token savings)."
    ),
    ExampleTask(
        id="ex2",
        title="2. Category B: Conceptual Reasoning",
        category="Category B: Conceptual LLM Reasoning",
        task="Explain the difference between TCP and UDP.",
        expected_tool="LLM Engine (No tools)",
        description="Direct LLM task. Shows JEV decision check trade-off (no tools needed; slight decision metadata overhead)."
    ),
    ExampleTask(
        id="ex3",
        title="3. Category C: Live External Info",
        category="Category C: External Info / Tools",
        task="Find the current weather in Bangalore.",
        expected_tool="Web Search API",
        description="Requires live data. OpenJEV fetches satellite weather data."
    ),
    ExampleTask(
        id="ex4",
        title="4. Category D: Mixed Multi-step",
        category="Category D: Mixed / Multi-step Tasks",
        task="What is 12345 * 67890 and explain the result?",
        expected_tool="Calculator + LLM",
        description="Requires exact numerical arithmetic followed by natural language explanation."
    ),
    ExampleTask(
        id="ex5",
        title="5. Category E: Code & Architecture",
        category="Category E: Complex Code / Architecture",
        task="Write a Python function that finds the longest substring without repeating characters and explain the complexity.",
        expected_tool="LLM Engine",
        description="Structured code generation. OpenJEV prunes unnecessary tool calls."
    )
]

@router.get("/examples", response_model=List[ExampleTask])
def get_example_tasks():
    return PREDEFINED_EXAMPLES

@router.post("/run", response_model=AgentRunResult)
async def run_agent(payload: TaskRequest):
    if not payload.task.strip():
        raise HTTPException(status_code=400, detail="Task string cannot be empty.")
    return await run_jev_agent(payload.task, provider=payload.provider)

@router.post("/compare", response_model=ComparisonResult)
async def compare_workflows(payload: TaskRequest):
    task = payload.task.strip()
    if not task:
        raise HTTPException(status_code=400, detail="Task string cannot be empty.")
    
    num_runs = max(1, min(10, payload.runs or 3))
    provider = payload.provider or "groq"

    naive_runs: List[AgentRunResult] = []
    jev_runs: List[AgentRunResult] = []

    for _ in range(num_runs):
        n_res, j_res = await asyncio.gather(
            run_naive_agent(task, provider=provider),
            run_jev_agent(task, provider=provider)
        )
        naive_runs.append(n_res)
        jev_runs.append(j_res)

    agg_naive = aggregate_agent_results(naive_runs, provider=provider)
    agg_jev = aggregate_agent_results(jev_runs, provider=provider)
    comparison = calculate_comparison_metrics(agg_naive, agg_jev, provider=provider, runs=num_runs)

    return ComparisonResult(
        timestamp=datetime.now().isoformat(),
        task=task,
        provider=provider,
        runs=num_runs,
        baseline_naive=agg_naive,
        optimized_jev=agg_jev,
        comparison=comparison
    )

@router.post("/benchmark", response_model=BenchmarkSuiteResult)
async def run_benchmark_suite(payload: Optional[TaskRequest] = None):
    provider = payload.provider if payload and payload.provider else "groq"
    num_runs = max(1, min(5, payload.runs if payload and payload.runs else 2))

    suite_results: List[ComparisonResult] = []
    for ex in PREDEFINED_EXAMPLES:
        req = TaskRequest(task=ex.task, provider=provider, runs=num_runs)
        res = await compare_workflows(req)
        suite_results.append(res)

    p_info = MODEL_PRICING.get(provider.lower(), MODEL_PRICING["groq"])

    return BenchmarkSuiteResult(
        timestamp=datetime.now().isoformat(),
        provider=provider,
        runs_per_task=num_runs,
        pricing_model=p_info,
        results=suite_results
    )

@router.post("/decision", response_model=JevDecisionResponse)
async def get_decision_only(payload: TaskRequest):
    task = payload.task.strip()
    if not task:
        raise HTTPException(status_code=400, detail="Task string cannot be empty.")
    decision, _ = await evaluate_task_with_openjev(task)
    return decision
