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

    # CORS
    cors_origins: str = "http://localhost:5173"

    # Rate limiting
    rate_limit_enabled: bool = True
    chat_rate_limit: str = "10/minute"
    intelligence_rate_limit: str = "5/minute"

    # Bright Data (disabled by default)
    brightdata_enabled: bool = False
    brightdata_api_key: str = ""
    brightdata_provider: str = "serp_api"
    brightdata_serp_endpoint: str = ""
    brightdata_serp_zone: str = "serp_api1"
    brightdata_web_unlocker_endpoint: str = ""
    brightdata_timeout_seconds: float = 60.0
    brightdata_max_results: int = 5
    brightdata_country: str = "us"
    brightdata_language: str = "en"

    # Bright Data MCP (alternative provider mode)
    brightdata_mcp_enabled: bool = False
    brightdata_mcp_command: str = "npx"
    brightdata_mcp_package: str = "@brightdata/mcp"
    brightdata_mcp_timeout_seconds: int = 90
    brightdata_mcp_max_results: int = 5

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
