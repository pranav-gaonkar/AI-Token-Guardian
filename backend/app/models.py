from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class TaskRequest(BaseModel):
    task: str = Field(..., json_schema_extra={"example": "Calculate 27 * 43"})
    provider: Optional[str] = "groq"

class OpenJEVQuestionAnswer(BaseModel):
    answer: Any
    type: str
    confidence: Optional[float] = None
    raw: Optional[Any] = None

class JevDecisionResponse(BaseModel):
    needs_external_information: bool = False
    required_tool: str = "none"
    needs_llm: bool = True
    needs_verification: bool = False
    task_complexity: float = 0.5
    raw_answers: Dict[str, Any] = {}
    decision_source: str = "OpenJEV"
    fallback_occurred: bool = False
    fallback_reason: Optional[str] = None

class ExecutionPlan(BaseModel):
    use_calculator: bool = False
    use_web_search: bool = False
    use_llm: bool = True
    verify: bool = False

class StepTrace(BaseModel):
    step: str
    status: str
    details: Optional[str] = None
    latency_ms: float = 0.0

class MetricStats(BaseModel):
    total_workflow_steps: int = 0
    openjev_calls: int = 0
    groq_calls: int = 0
    tool_calls: int = 0
    estimated_input_tokens: int = 0
    estimated_output_tokens: int = 0
    total_estimated_tokens: int = 0
    latency_ms: float = 0.0
    fallback_occurred: bool = False
    is_estimated: bool = True

class AgentRunResult(BaseModel):
    task: str
    jev_decision: JevDecisionResponse
    execution_plan: ExecutionPlan
    trace: List[StepTrace]
    tool_results: Dict[str, Any]
    final_answer: str
    metrics: MetricStats

class ComparisonMetrics(BaseModel):
    llm_calls_avoided: int = 0
    tool_calls_avoided: int = 0
    token_saved: int = 0
    token_reduction_percentage: Optional[float] = None
    latency_diff_ms: float = 0.0
    latency_reduction_percentage: Optional[float] = None
    estimated_cost_saved_usd: float = 0.0
    estimated_cost_saved_10k_usd: float = 0.0

class ComparisonResult(BaseModel):
    task: str
    baseline_naive: AgentRunResult
    optimized_jev: AgentRunResult
    comparison: ComparisonMetrics

class ExampleTask(BaseModel):
    id: str
    title: str
    task: str
    expected_tool: str
    description: str
