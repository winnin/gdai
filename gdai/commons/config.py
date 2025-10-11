"""Centralized configuration for all GDAI components.

This module provides an organized configuration structure with environment variable loading,
validation, and access to settings organized by component.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

# Loads environment variables with override to prioritize local .env file
load_dotenv(override=True)

# Sets up logger for configuration
logger = logging.getLogger("GDAI_CONFIG")


class ConfigComponent:
    """Base class for configuration components with validation support."""

    @classmethod
    def validate(cls) -> bool:
        """Default validation method to be overridden by subclasses.

        Returns:
            bool: True if the configuration is valid
        """
        return True


class DatabaseConfig(ConfigComponent):
    """Database connection configuration."""

    DATABASE = os.getenv("DATABASE")

    # PGVector settings
    PGVECTOR_USER = os.getenv("PGVECTOR_USER")
    PGVECTOR_PASSWORD = os.getenv("PGVECTOR_PASSWORD")
    PGVECTOR_DATABASE = os.getenv("PGVECTOR_DATABASE")
    PGVECTOR_HOST = os.getenv("PGVECTOR_HOST")
    PGVECTOR_PORT = int(os.getenv("PGVECTOR_PORT", "5432"))
    PGVECTOR_MIN_POOL_CONNECTIONS = int(os.getenv("PGVECTOR_MIN_POOL_CONNECTIONS", "2"))
    PGVECTOR_MAX_POOL_CONNECTIONS = int(os.getenv("PGVECTOR_MAX_POOL_CONNECTIONS", "10"))

    @classmethod
    def validate(cls) -> bool:
        """Validates the database configuration."""
        if not cls.DATABASE:
            logger.error("DATABASE is not set")
            return False

        if not cls.PGVECTOR_USER:
            logger.error("PGVECTOR_USER is not set")
            return False
        if not cls.PGVECTOR_PASSWORD:
            logger.error("PGVECTOR_PASSWORD is not set")
            return False
        if not cls.PGVECTOR_DATABASE:
            logger.error("PGVECTOR_DATABASE is not set")
            return False
        if not cls.PGVECTOR_HOST:
            logger.error("PGVECTOR_HOST is not set")
            return False
        if cls.PGVECTOR_MIN_POOL_CONNECTIONS < 0:
            logger.error("PGVECTOR_MIN_POOL_CONNECTIONS is misconfigured")
            return False
        if cls.PGVECTOR_MAX_POOL_CONNECTIONS < 0:
            logger.error("PGVECTOR_MAX_POOL_CONNECTIONS is misconfigured")
            return False

        return True


class LLMConfig(ConfigComponent):
    """AI models configuration."""

    LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-4o")
    LLM_MODEL_API_KEY = os.getenv("LLM_API_KEY")
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1000"))
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))

    @classmethod
    def validate(cls) -> bool:
        """Validates the AI models configuration."""
        if not cls.LLM_MODEL:
            logger.error("LLM_MODEL is not set")
            return False
        if not cls.LLM_MODEL_API_KEY:
            logger.error("LLM_API_KEY is not set")
            return False
        if cls.LLM_MAX_TOKENS <= 0:
            logger.error("LLM_MAX_TOKENS must be positive")
            return False
        if not (0 <= cls.LLM_TEMPERATURE <= 1.0):
            logger.error("LLM_TEMPERATURE must be between 0.0 and 1.0")
            return False

        return True


class ExtractorConfig(ConfigComponent):
    """Document extractor configuration."""

    TMP_FOLDER = os.getenv("EXTRACTOR_TMP_FOLDER")
    MAX_FILE_SIZE_MB = int(os.getenv("EXTRACTOR_MAX_FILE_SIZE_MB", "100"))
    MAX_RETRIES = int(os.getenv("EXTRACTOR_MAX_RETRIES", "3"))

    @classmethod
    def validate(cls) -> bool:
        """Validates the document extractor configuration."""
        if not cls.TMP_FOLDER:
            logger.error("EXTRACTOR_TMP_FOLDER is not set")
            return False

        raw_path = Path(cls.TMP_FOLDER)
        if not raw_path.exists():
            logger.warning(f"Raw documents directory does not exist: {cls.TMP_FOLDER}")
            # create the directory
            try:
                raw_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Directory created: {cls.TMP_FOLDER}")
            except Exception as e:
                logger.error(f"Could not create directory: {e}")
                raise e

        if cls.MAX_FILE_SIZE_MB <= 0:
            logger.error("MAX_FILE_SIZE_MB must be a positive value")
            return False
        if cls.MAX_RETRIES < 0:
            logger.error("EXTRACTOR_MAX_RETRIES must be a non-negative value")
            return False

        return True


class EmbeddingConfig(ConfigComponent):
    """Document embedding service configuration."""

    MAX_TEXT_SIZE = int(os.getenv("EMBEDDING_MAX_TEXT_SIZE") or 0)
    MAX_RETRIES = int(os.getenv("EMBEDDING_MAX_RETRIES") or 0)
    BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE") or 64)
    DIMENSION = int(os.getenv("EMBEDDING_DIMENSION"))
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
    EMBEDDING_MODEL_API_KEY = os.getenv("EMBEDDING_API_KEY")  # Use EMBEDDING_API_KEY from .env

    @classmethod
    def validate(cls) -> bool:
        if cls.MAX_TEXT_SIZE <= 0:
            logger.error("EMBEDDING_MAX_TEXT_SIZE must be a positive value")
            return False
        if cls.MAX_RETRIES < 0:
            logger.error("EMBEDDING_MAX_RETRIES must be a non-negative value")
            return False
        if cls.BATCH_SIZE <= 0:
            logger.error("EMBEDDING_BATCH_SIZE must be a positive value")
            return False
        if cls.DIMENSION <= 0:
            logger.error("EMBEDDING_DIMENSION must be a positive value")
            return False
        if not cls.EMBEDDING_MODEL:
            logger.error("EMBEDDING_MODEL is not set")
            return False
        if not cls.EMBEDDING_MODEL_API_KEY:
            logger.error("EMBEDDING_MODEL_API_KEY is not set")
            return False

        return True


class Config:
    """Main configuration class that groups all components.

    This class serves as the central access point for all configurations
    and provides validation methods for all configuration.
    """

    # Configuration components
    db = DatabaseConfig
    llm = LLMConfig
    extractor = ExtractorConfig
    embedding = EmbeddingConfig

    # Add this dictionary to map component names to their configuration classes
    _components = {
        "db": DatabaseConfig,
        "llm": LLMConfig,
        "extractor": ExtractorConfig,
        "embedding": EmbeddingConfig,
    }

    @classmethod
    def validate_all(cls) -> bool:
        """Validates all configuration components.

        Returns:
            bool: True if all components are valid, False otherwise
        """
        all_valid = True

        for name, component in cls._components.items():
            logger.info(f"Validating configuration for {name}...")
            if not component.validate():
                logger.error(f"Configuration validation for {name.upper()} failed")
                all_valid = False
            else:
                logger.info(f"Configuration for {name.upper()} validated successfully")

        if all_valid:
            logger.info("All configurations validated successfully")
        else:
            logger.error("Configuration validation failed")

        return all_valid

    @classmethod
    def get_component(cls, component_name: str) -> type[ConfigComponent] | None:
        """Gets a configuration component by name.

        Args:
            component_name: The name of the component to retrieve

        Returns:
            The configuration component class or None if not found
        """
        return cls._components.get(component_name.lower())


# Validate all configurations when importing this module
Config.validate_all()
