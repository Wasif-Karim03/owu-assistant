from pathlib import Path

from pydantic_settings import BaseSettings

_ROOT_DIR = Path(__file__).resolve().parent.parent.parent
_ENV_FILES = [str(_ROOT_DIR / ".env"), ".env"]


class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/owu_assistant"
    FRONTEND_URL: str = "http://localhost:3000"
    ENVIRONMENT: str = "development"

    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 100
    TOP_K_RESULTS: int = 6

    EMBEDDING_MODEL: str = "text-embedding-3-small"
    CHAT_MODEL: str = "gpt-4o-mini"

    model_config = {"env_file": _ENV_FILES, "extra": "ignore"}


settings = Settings()
