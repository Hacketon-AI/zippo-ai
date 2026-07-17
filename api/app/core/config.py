from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # App
    app_name: str = "personal-ai-assistant"
    app_env: str = "development"

    # API
    api_prefix: str = "/api/v1"

    # Ollama (local)
    ollama_base_url: str = "http://ollama:11434"
    ollama_default_model: str = "qwen3:4b"
    ollama_timeout_seconds: float = 60.0
    ollama_embed_model: str = "nomic-embed-text"
    ollama_embed_timeout_seconds: float = 60.0

    # Ollama generation tuning.
    # Sampling defaults follow Qwen3's recommendation for non-thinking mode
    # (temperature 0.7, top_p 0.8); thinking mode would want 0.6/0.95.
    ollama_num_ctx: int = 8192  # default Ollama 2048 kepotong oleh persona+memory
    ollama_temperature: float = 0.7
    ollama_top_p: float = 0.8
    ollama_repeat_penalty: float = 1.1
    ollama_think: bool = False  # qwen3 thinking mode: lambat, boros token

    # OpenRouter (cloud LLM — set use_openrouter=true to enable)
    use_openrouter: bool = False
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "qwen/qwen3-235b-a22b"
    openrouter_timeout_seconds: float = 120.0

    # PostgreSQL
    database_url: str = (
        "postgresql+asyncpg://changeme:changeme@postgres:5432/personal_ai"
    )

    # Cache
    cache_ttl_seconds: int = 86400  # 24h default; 0 or negative disables expiry

    # Qdrant
    qdrant_url: str = "http://qdrant:6333"
    qdrant_collection: str = "personal_ai_memory"
    qdrant_vector_size: int = 768
    qdrant_search_limit: int = 5
    qdrant_score_threshold: float = 0.75

    # CORS
    cors_origins: str = "http://localhost:5173"

    # Rate limiting
    rate_limit_enabled: bool = True
    chat_rate_limit: str = "10/minute"

    # Auth
    auth_session_ttl_hours: int = 168  # 7 days
    login_rate_limit: str = "5/minute"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached Settings instance."""
    return Settings()
