from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # App
    app_name: str = "personal-ai-assistant"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "info"

    # API
    api_prefix: str = "/api/v1"

    # Ollama
    ollama_base_url: str = "http://ollama:11434"
    ollama_default_model: str = "qwen3:4b"
    ollama_timeout_seconds: float = 60.0
    ollama_embed_model: str = "nomic-embed-text"
    ollama_embed_timeout_seconds: float = 60.0

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

    # External fallback (disabled by default)
    external_fallback_enabled: bool = False
    external_fallback_provider: str = "none"
    external_fallback_api_key: str = ""
    external_fallback_timeout_seconds: float = 60.0

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
