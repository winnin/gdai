"""Application settings using Pydantic Settings."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""

    model_config = SettingsConfigDict(env_prefix="PGVECTOR_", case_sensitive=False)

    database: str = Field(..., description="Database name")
    user: str = Field(..., description="Database user")
    password: str = Field(..., description="Database password")
    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, description="Database port")
    min_pool_connections: int = Field(default=5, gt=0, description="Minimum pool size")
    max_pool_connections: int = Field(default=20, gt=0, description="Maximum pool size")

    @field_validator("max_pool_connections")
    @classmethod
    def validate_pool_size(cls, v: int, info) -> int:
        """Validate that max_pool is greater than min_pool."""
        if "min_pool_connections" in info.data and v <= info.data["min_pool_connections"]:
            raise ValueError("max_pool_connections must be greater than min_pool_connections")
        return v

    def get_url(self) -> str:
        """Get database connection URL.

        Returns:
            str: PostgreSQL connection URL for asyncpg.
        """
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class EmbeddingSettings(BaseSettings):
    """Embedding model configuration settings."""

    model_config = SettingsConfigDict(env_prefix="EMBEDDING_", case_sensitive=False)

    model: str = Field(..., description="Embedding model name")
    model_api_key: str = Field(..., description="API key for embedding service")
    dimension: int = Field(..., gt=0, description="Embedding dimension")
    max_text_size: int = Field(default=5000, gt=0, description="Maximum text size for embedding")
    batch_size: int = Field(default=96, gt=0, description="Maximum batch size")
    max_retries: int = Field(default=3, ge=0, description="Maximum retry attempts")

    @field_validator("dimension")
    @classmethod
    def validate_dimension(cls, v: int) -> int:
        """Validate embedding dimension."""
        if v <= 0:
            raise ValueError("Embedding dimension must be positive")
        return v


class LLMSettings(BaseSettings):
    """LLM configuration settings."""

    model_config = SettingsConfigDict(env_prefix="LLM_", case_sensitive=False)

    model: str = Field(..., description="LLM model name")
    api_key: str = Field(..., description="API key for LLM service")
    max_tokens: int = Field(default=2000, gt=0, description="Maximum tokens for generation")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Temperature for generation")

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        """Validate temperature range."""
        if not 0.0 <= v <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        return v


class ExtractorSettings(BaseSettings):
    """Extractor configuration settings."""

    model_config = SettingsConfigDict(env_prefix="", case_sensitive=False)

    tmp_folder: str = Field(default="/tmp", description="Temporary folder for file processing")
    max_file_size_mb: int = Field(default=100, gt=0, description="Maximum file size in MB")
    max_retries: int = Field(default=3, ge=0, description="Maximum retry attempts")

    @field_validator("tmp_folder")
    @classmethod
    def validate_tmp_folder(cls, v: str) -> str:
        """Validate tmp folder exists."""
        import os

        if not os.path.exists(v):
            try:
                os.makedirs(v, exist_ok=True)
            except Exception as e:
                raise ValueError(f"Cannot create tmp folder {v}: {e}")
        return v


class TemporalSettings(BaseSettings):
    """Temporal configuration settings."""

    model_config = SettingsConfigDict(env_prefix="TEMPORAL_", case_sensitive=False)

    host: str = Field(default="localhost:7233", description="Temporal server host")
    namespace: str = Field(default="default", description="Temporal namespace")
    task_queue: str = Field(default="gdai-task-queue", description="Default task queue")


class Settings:
    """Main application settings container."""

    def __init__(self):
        """Initialize all settings from environment variables."""
        self.database = DatabaseSettings()
        self.embedding = EmbeddingSettings()
        self.llm = LLMSettings()
        self.extractor = ExtractorSettings()
        self.temporal = TemporalSettings()

        # Application settings - read from environment or use defaults
        import os

        self.app_name = os.getenv("APP_NAME", "GDAI")
        self.debug = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        Settings: Application settings instance.
    """
    return Settings()
