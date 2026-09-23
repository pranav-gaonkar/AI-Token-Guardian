from fastapi import APIRouter, HTTPException
from typing import List
from app.models import (
    TaskRequest, AgentRunResult, ComparisonResult, JevDecisionResponse, ExampleTask
)
from app.services.agent_runner import run_jev_agent, run_naive_agent
from app.services.openjev_service import evaluate_task_with_openjev
from app.services.metrics import calculate_comparison_metrics

router = APIRouter(prefix="/api", tags=["Agent Analysis"])

PREDEFINED_EXAMPLES: List[ExampleTask] = [
    ExampleTask(
        id="ex1",
        title="1. Pure Calculation",
        task="Calculate 27 * 43.",
        expected_tool="Calculator (LLM avoided)",
        description="Deterministic mathematical expression. OpenJEV routes to calculator directly and skips Groq LLM."
    ),
    ExampleTask(
        id="ex2",
        title="2. LLM Conceptual Explanation",
        task="Explain the difference between TCP and UDP.",
        expected_tool="Groq LLM (No tools required)",
        description="Requires natural language reasoning. OpenJEV determines external search and calculator are not required."
    ),
    ExampleTask(
        id="ex3",
        title="3. Live External Information",
        task="Find the current weather in Bangalore.",
        expected_tool="Web Search + Groq LLM",
        description="Requires external real-time data. OpenJEV selects Web Search tool and LLM synthesis."
    ),
    ExampleTask(
        id="ex4",
        title="4. Code Synthesis & Analysis",
        task="Write a Python function that finds the longest substring without repeating characters and explain the complexity.",
        expected_tool="Groq LLM",
        description="Complex reasoning request requiring structured code generation."
    ),
    ExampleTask(
        id="ex5",
        title="5. Large Calculation + Explanation",
        task="What is 12345 * 67890 and explain the result?",
        expected_tool="Calculator + Groq LLM",
        description="Requires exact numerical arithmetic followed by natural language explanation."
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
    
    import asyncio
    naive_res, jev_res = await asyncio.gather(
        run_naive_agent(task, provider=payload.provider),
        run_jev_agent(task, provider=payload.provider)
    )
    comparison = calculate_comparison_metrics(naive_res, jev_res)

    return ComparisonResult(
        task=task,
        baseline_naive=naive_res,
        optimized_jev=jev_res,
        comparison=comparison
    )

@router.post("/decision", response_model=JevDecisionResponse)
async def get_decision_only(payload: TaskRequest):
    task = payload.task.strip()
    if not task:
        raise HTTPException(status_code=400, detail="Task string cannot be empty.")
    decision, _ = await evaluate_task_with_openjev(task)
    return decision
