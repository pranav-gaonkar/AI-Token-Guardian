from typing import Dict, Any

def build_openjev_payload(user_request: str) -> Dict[str, Any]:
    return {
        "model": "openjev",
        "state": {
            "user_request": user_request,
            "available_tools": [
                "calculator",
                "web_search",
                "groq_llm"
            ],
            "objective": "answer the user accurately while minimizing unnecessary operations"
        },
        "questions": {
            "needs_external_information": {
                "type": "noul",
                "instructions": "Does this request require information that cannot reliably be answered from the request/context alone?"
            },
            "required_tool": {
                "type": "choice",
                "instructions": "Which specific tool is required to process or resolve this task?",
                "choices": [
                    "none",
                    "calculator",
                    "web_search"
                ],
                "criteria": {
                    "none": "No special external tool or calculator is needed.",
                    "calculator": "Exact mathematical computation, arithmetic, or numeric evaluation is needed.",
                    "web_search": "Live web data, recent events, stock prices, weather, or real-time info is needed."
                }
            },
            "needs_llm": {
                "type": "noul",
                "instructions": "Does the final response require language generation or complex reasoning from an LLM?"
            },
            "needs_verification": {
                "type": "noul",
                "instructions": "Would an additional verification step materially improve output reliability?"
            },
            "task_complexity": {
                "type": "score",
                "instructions": "Rate the complexity of this task from 0 (trivial/simple math or exact tool lookup) to 1 (highly complex multi-step reasoning).",
                "criteria": [
                    "0 is trivial/simple arithmetic or exact lookup",
                    "1 is highly complex multi-step reasoning"
                ]
            }
        }
    }

