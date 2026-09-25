import os
from pathlib import Path
from dotenv import load_dotenv

backend_dir = Path(__file__).resolve().parent.parent
root_dir = backend_dir.parent

load_dotenv(backend_dir / ".env")
load_dotenv(root_dir / ".env")

def _reload_env():
    load_dotenv(backend_dir / ".env", override=True)
    load_dotenv(root_dir / ".env", override=True)

class Settings:
    @property
    def OPENJEV_API_KEY(self) -> str:
        _reload_env()
        return os.getenv("OPENJEV_API_KEY", "").strip()

    @property
    def GROQ_API_KEY(self) -> str:
        _reload_env()
        return os.getenv("GROQ_API_KEY", "").strip()

    @property
    def GROQ_MODEL(self) -> str:
        _reload_env()
        return os.getenv("GROQ_MODEL", "openai/gpt-oss-20b").strip()

    @property
    def OPENAI_API_KEY(self) -> str:
        _reload_env()
        return os.getenv("OPENAI_API_KEY", "").strip()

    @property
    def OPENAI_MODEL(self) -> str:
        _reload_env()
        return os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()

    @property
    def LLM_PROVIDER(self) -> str:
        _reload_env()
        return os.getenv("LLM_PROVIDER", "groq").strip().lower()

    @property
    def OPENJEV_URL(self) -> str:
        _reload_env()
        return os.getenv("OPENJEV_URL", "https://api.openjev.sh/v1/systemone").strip()

    @property
    def has_openjev_key(self) -> bool:
        return bool(self.OPENJEV_API_KEY)

    @property
    def has_groq_key(self) -> bool:
        return bool(self.GROQ_API_KEY)

    @property
    def GEMINI_API_KEY(self) -> str:
        _reload_env()
        return os.getenv("GEMINI_API_KEY", "").strip()

    @property
    def GEMINI_MODEL(self) -> str:
        _reload_env()
        return os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite").strip()

    @property
    def has_openai_key(self) -> bool:
        return bool(self.OPENAI_API_KEY)

    @property
    def has_gemini_key(self) -> bool:
        return bool(self.GEMINI_API_KEY)

settings = Settings()
