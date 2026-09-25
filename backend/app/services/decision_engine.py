import logging
from app.models import JevDecisionResponse, ExecutionPlan

logger = logging.getLogger(__name__)

def build_execution_plan(decision: JevDecisionResponse, task: str) -> ExecutionPlan:
    use_calc = decision.required_tool == "calculator"
    use_search = decision.required_tool == "web_search" or decision.needs_external_information
    use_llm = decision.needs_llm
    verify = decision.needs_verification

    if not use_calc and not use_search and not use_llm:
        logger.warning("Contradiction detected: No tools selected and needs_llm=False. Overriding use_llm to True.")
        use_llm = True



    return ExecutionPlan(
        use_calculator=use_calc,
        use_web_search=use_search,
        use_llm=use_llm,
        verify=verify
    )
