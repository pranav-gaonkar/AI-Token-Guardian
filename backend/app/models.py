from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class TaskRequest(BaseModel):
    task: str = Field(..., json_schema_extra={"example": "Calculate 27 * 43"})
    provider: Optional[str] = "groq"
    runs: Optional[int] = 3

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
    openjev_calls: float = 0.0
    groq_calls: float = 0.0
    tool_calls: float = 0.0
    estimated_input_tokens: int = 0
    estimated_output_tokens: int = 0
    total_estimated_tokens: int = 0
    latency_ms: float = 0.0
    min_latency_ms: Optional[float] = None
    max_latency_ms: Optional[float] = None
    fallback_occurred: bool = False
    is_estimated: bool = True
    token_source: str = "estimated"
    cost_usd: float = 0.0

class AgentRunResult(BaseModel):
    task: str
    jev_decision: JevDecisionResponse
    execution_plan: ExecutionPlan
    trace: List[StepTrace]
    tool_results: Dict[str, Any]
    final_answer: str
    metrics: MetricStats

class ComparisonMetrics(BaseModel):
    runs: int = 1
    llm_calls_avoided: float = 0.0
    tool_calls_avoided: float = 0.0
    token_saved: float = 0.0
    token_reduction_percentage: Optional[float] = None
    latency_diff_ms: float = 0.0
    latency_change_percentage: Optional[float] = None
    naive_avg_latency_ms: float = 0.0
    naive_min_latency_ms: float = 0.0
    naive_max_latency_ms: float = 0.0
    jev_avg_latency_ms: float = 0.0
    jev_min_latency_ms: float = 0.0
    jev_max_latency_ms: float = 0.0
    estimated_cost_saved_usd: float = 0.0
    estimated_cost_saved_10k_usd: float = 0.0
    pricing_model: Dict[str, float] = {}
    provider: str = "groq"
    token_source: str = "estimated"

class ComparisonResult(BaseModel):
    timestamp: Optional[str] = None
    task: str
    provider: str = "groq"
    runs: int = 1
    baseline_naive: AgentRunResult
    optimized_jev: AgentRunResult
    comparison: ComparisonMetrics

class ExampleTask(BaseModel):
    id: str
    title: str
    category: str
    task: str
    expected_tool: str
    description: str

class BenchmarkSuiteResult(BaseModel):
    timestamp: str
    provider: str
    runs_per_task: int
    pricing_model: Dict[str, float]
    results: List[ComparisonResult]
