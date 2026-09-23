from fastapi import APIRouter
from app.config import settings

router = APIRouter()

@router.get("/health")
def check_health():
    return {
        "status": "healthy",
        "service": "AI Token Guardian Backend",
        "version": "1.0.0",
        "config": {
            "has_openjev_key": settings.has_openjev_key,
            "has_groq_key": settings.has_groq_key,
            "has_openai_key": settings.has_openai_key,
            "groq_model": settings.GROQ_MODEL,
            "openai_model": settings.OPENAI_MODEL,
            "llm_provider": settings.LLM_PROVIDER,
            "openjev_url": settings.OPENJEV_URL
        }
    }
