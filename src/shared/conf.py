"""
Centralized configuration for all G-DAI components.

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
        """
        Default validation method to be overridden by subclasses.

        Returns:
            bool: True if the configuration is valid
        """
        return True


class DatabaseConfig(ConfigComponent):
    """Database connection configuration."""

    # PGVector settings
    PGVECTOR_USER = os.getenv("PGVECTOR_USER")
    PGVECTOR_PASSWORD = os.getenv("PGVECTOR_PASSWORD")
    PGVECTOR_DATABASE = os.getenv("PGVECTOR_DATABASE")
    PGVECTOR_HOST = os.getenv("PGVECTOR_HOST")
    PGVECTOR_PORT = int(os.getenv("PGVECTOR_PORT", "5432"))
    PGVECTOR_MIN_POOL_CONNECTIONS = int(os.getenv("PGVECTOR_MIN_POOL_CONNECTIONS", "2"))
    PGVECTOR_MAX_POOL_CONNECTIONS = int(
        os.getenv("PGVECTOR_MAX_POOL_CONNECTIONS", "10")
    )

    @classmethod
    def validate(cls) -> bool:
        """Validates the database configuration."""
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


class BrokerConfig(ConfigComponent):
    """Message broker configuration."""

    # RabbitMQ settings
    RABBIT_MQ_HOST = os.getenv("RABBIT_MQ_HOST")
    RABBIT_MQ_PORT = int(os.getenv("RABBIT_MQ_PORT", "5672"))
    RABBIT_MQ_USER = os.getenv("RABBIT_MQ_USER")
    RABBIT_MQ_PASSWORD = os.getenv("RABBIT_MQ_PASSWORD")

    @classmethod
    def validate(cls) -> bool:
        """Validates the message broker configuration."""
        if not cls.RABBIT_MQ_HOST:
            logger.error("RABBIT_MQ_HOST is not set")
            return False
        if cls.RABBIT_MQ_PORT < 0:
            logger.error("RABBIT_MQ_PORT is invalid")
            return False
        if not cls.RABBIT_MQ_USER:
            logger.error("RABBIT_MQ_USER is not set")
            return False
        if not cls.RABBIT_MQ_PASSWORD:
            logger.error("RABBIT_MQ_PASSWORD is not set")
            return False

        return True


class AIModelsConfig(ConfigComponent):
    """AI models configuration."""

    # Embedding model settings
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "cohere/embed-v4.0")
    EMBEDDING_MODEL_API_KEY = os.getenv("EMBEDDING_API_KEY")

    # LLM model settings
    LLM_MODEL = os.getenv("SEARCH_LLM_MODEL", "openai/gpt-4o")
    LLM_MODEL_API_KEY = os.getenv("SEARCH_LLM_API_KEY")
    LLM_MAX_TOKENS = int(os.getenv("SEARCH_LLM_MAX_TOKENS", "1000"))
    LLM_TEMPERATURE = float(os.getenv("SEARCH_LLM_TEMPERATURE", "0.7"))

    @classmethod
    def validate(cls) -> bool:
        """Validates the AI models configuration."""
        if not cls.EMBEDDING_MODEL:
            logger.error("EMBEDDING_MODEL is not set")
            return False
        if not cls.EMBEDDING_MODEL_API_KEY:
            logger.error("EMBEDDING_API_KEY is not set")
            return False
        if not cls.LLM_MODEL:
            logger.error("SEARCH_LLM_MODEL is not set")
            return False
        if not cls.LLM_MODEL_API_KEY:
            logger.error("SEARCH_LLM_API_KEY is not set")
            return False
        if cls.LLM_MAX_TOKENS <= 0:
            logger.error("SEARCH_LLM_MAX_TOKENS must be positive")
            return False
        if not (0 <= cls.LLM_TEMPERATURE <= 1.0):
            logger.error("SEARCH_LLM_TEMPERATURE must be between 0.0 and 1.0")
            return False

        return True


class ExtractorConfig(ConfigComponent):
    """Document extractor configuration."""

    FOLDER_RAW_DOC_PATH = os.getenv("DOCUMENT_EXTRACTOR_FOLDER_SOURCE_PATH")
    FOLDER_EXTRACTED_DOC_PATH = os.getenv("DOCUMENT_EXTRACTOR_FOLDER_TARGET_PATH")
    MAX_FILE_SIZE_MB = int(os.getenv("DOCUMENT_EXTRACTOR_MAX_FILE_SIZE_MB", "100"))
    EXTRACTOR = os.getenv("DOCUMENT_EXTRACTOR", "docling")
    MAX_RETRIES = int(os.getenv("DOCUMENT_EXTRACTOR_MAX_RETRIES", "3"))
    RETRY_DELAY = int(os.getenv("DOCUMENT_EXTRACTOR_RETRY_DELAY", "5"))
    QUEUE = os.getenv("DOCUMENT_EXTRACTOR_QUEUE")

    @classmethod
    def validate(cls) -> bool:
        """Validates the document extractor configuration."""
        if not cls.FOLDER_RAW_DOC_PATH:
            logger.error("DOCUMENT_EXTRACTOR_FOLDER_RAW_DOC_PATH is not set")
            return False

        raw_path = Path(cls.FOLDER_RAW_DOC_PATH)
        if not raw_path.exists():
            logger.warning(
                f"Raw documents directory does not exist: {cls.FOLDER_RAW_DOC_PATH}"
            )
            # Try to create the directory
            try:
                raw_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Directory created: {cls.FOLDER_RAW_DOC_PATH}")
            except Exception as e:
                logger.error(f"Could not create directory: {e}")
                return False

        if not cls.FOLDER_EXTRACTED_DOC_PATH:
            logger.error("DOCUMENT_EXTRACTOR_FOLDER_EXTRACTED_DOC_PATH is not set")
            return False

        extracted_path = Path(cls.FOLDER_EXTRACTED_DOC_PATH)
        if not extracted_path.exists():
            logger.warning(
                f"Extracted documents directory does not exist: {cls.FOLDER_EXTRACTED_DOC_PATH}"
            )
            # Try to create the directory
            try:
                extracted_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Directory created: {cls.FOLDER_EXTRACTED_DOC_PATH}")
            except Exception as e:
                logger.error(f"Could not create directory: {e}")
                return False

        if cls.MAX_FILE_SIZE_MB <= 0:
            logger.error("MAX_FILE_SIZE_MB must be a positive value")
            return False
        if cls.MAX_RETRIES < 0:
            logger.error("DOCUMENT_EXTRACTOR_MAX_RETRIES must be a non-negative value")
            return False
        if cls.RETRY_DELAY < 0:
            logger.error("DOCUMENT_EXTRACTOR_RETRY_DELAY must be a non-negative value")
            return False

        if cls.QUEUE is None:
            logger.error("DOCUMENT_EXTRACTOR_QUEUE is not set")
            return False

        return True


class EmbeddingConfig(ConfigComponent):
    """Document embedding service configuration."""

    FOLDER_EXTRACTED_DOC_PATH = os.getenv("EMBEDDING_FOLDER_SOURCE_PATH")
    CHUNK_SIZE = int(os.getenv("EMBEDDING_CHUNK_SIZE"))
    CHUNK_OVERLAP = int(os.getenv("EMBEDDING_CHUNK_OVERLAP"))
    MAX_RETRIES = int(os.getenv("EMBEDDING_MAX_RETRIES"))
    RETRY_DELAY = int(os.getenv("EMBEDDING_RETRY_DELAY"))
    MAX_MEMORY_USAGE_PERCENT = int(os.getenv("EMBEDDING_MAX_MEMORY_USAGE_PERCENT"))
    QUEUE = os.getenv("EMBEDDING_QUEUE")

    @classmethod
    def validate(cls) -> bool:
        """Validates the embedding configuration."""
        if not cls.FOLDER_EXTRACTED_DOC_PATH:
            logger.error("EMBEDDING_FOLDER_SOURCE_PATH is not set")
            return False

        if not cls.FOLDER_EXTRACTED_DOC_PATH:
            logger.error("EMBEDDING_FOLDER_SOURCE_PATH is not set")
            return False

        if cls.CHUNK_SIZE <= 0:
            logger.error("EMBEDDING_CHUNK_SIZE must be a positive value")
            return False
        if cls.CHUNK_OVERLAP < 0:
            logger.error("EMBEDDING_CHUNK_OVERLAP must be a non-negative value")
            return False
        if cls.MAX_MEMORY_USAGE_PERCENT <= 0 or cls.MAX_MEMORY_USAGE_PERCENT > 100:
            logger.error("EMBEDDING_MAX_MEMORY_USAGE_PERCENT must be between 1 and 100")
            return False
        if cls.MAX_RETRIES < 0:
            logger.error("EMBEDDING_MAX_RETRIES must be a non-negative value")
            return False
        if cls.RETRY_DELAY < 0:
            logger.error("EMBEDDING_RETRY_DELAY must be a non-negative value")
            return False
        if cls.QUEUE is None:
            logger.error("EMBEDDING_QUEUE is not set")
            return False

        return True


class SearchConfig(ConfigComponent):
    """Search service configuration."""

    LLM_MAX_TOKENS = int(os.getenv("SEARCH_LLM_MAX_TOKENS"))
    LLM_TEMPERATURE = float(os.getenv("SEARCH_LLM_TEMPERATURE"))

    @classmethod
    def validate(cls) -> bool:
        """Validates the search configuration."""
        if cls.LLM_MAX_TOKENS < 0:
            logger.error("SEARCH_MAX_RETRIES must be a non-negative value")
            return False
        if cls.LLM_TEMPERATURE < 0:
            logger.error("SEARCH_RETRY_DELAY must be a non-negative value")
            return False

        return True


class Config:
    """
    Main configuration class that groups all components.

    This class serves as the central access point for all configurations
    and provides validation methods for all configuration.
    """

    # Configuration components
    db = DatabaseConfig
    broker = BrokerConfig
    ai = AIModelsConfig
    extractor = ExtractorConfig
    embedding = EmbeddingConfig
    search = SearchConfig

    # Component mapping
    _components = {
        "db": db,
        "broker": broker,
        "ai": ai,
        "extractor": extractor,
        "embedding": embedding,
        "search": search,
    }

    @classmethod
    def validate_all(cls) -> bool:
        """
        Validates all configuration components.

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
        """
        Gets a configuration component by name.

        Args:
            component_name: The name of the component to retrieve

        Returns:
            The configuration component class or None if not found
        """
        return cls._components.get(component_name.lower())


# Validate all configurations when importing this module
Config.validate_all()
