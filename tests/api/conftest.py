"""Pytest configuration for API tests."""

import os

import pytest


@pytest.fixture(autouse=True, scope="session")
def setup_test_env():
    """Set up test environment variables for API tests."""
    # Database settings
    os.environ.setdefault("PGVECTOR_DATABASE", "test_vectordb")
    os.environ.setdefault("PGVECTOR_USER", "testuser")
    os.environ.setdefault("PGVECTOR_PASSWORD", "testpwd")
    os.environ.setdefault("PGVECTOR_HOST", "localhost")
    os.environ.setdefault("PGVECTOR_PORT", "5555")
    os.environ.setdefault("PGVECTOR_MIN_POOL_CONNECTIONS", "2")
    os.environ.setdefault("PGVECTOR_MAX_POOL_CONNECTIONS", "10")

    # Embedding settings
    os.environ.setdefault("EMBEDDING_MODEL", "cohere/embed-v4.0")
    os.environ.setdefault("EMBEDDING_API_KEY", "fake-api-key-for-testing")
    os.environ.setdefault("EMBEDDING_DIMENSION", "1536")
    os.environ.setdefault("EMBEDDING_MAX_TEXT_SIZE", "5000")
    os.environ.setdefault("EMBEDDING_BATCH_SIZE", "96")
    os.environ.setdefault("EMBEDDING_MAX_RETRIES", "3")

    # LLM settings
    os.environ.setdefault("LLM_MODEL", "openai/gpt-4o")
    os.environ.setdefault("LLM_API_KEY", "fake-api-key-for-testing")
    os.environ.setdefault("LLM_MAX_TOKENS", "2000")
    os.environ.setdefault("LLM_TEMPERATURE", "0.7")

    # Extractor settings
    os.environ.setdefault("EXTRACTOR_TMP_FOLDER", "/tmp")
    os.environ.setdefault("EXTRACTOR_MAX_FILE_SIZE_MB", "100")
    os.environ.setdefault("EXTRACTOR_MAX_RETRIES", "3")

    # Temporal settings
    os.environ.setdefault("TEMPORAL_HOST", "localhost:7233")
    os.environ.setdefault("TEMPORAL_NAMESPACE", "default")
    os.environ.setdefault("TEMPORAL_TASK_QUEUE", "gdai-task-queue")

    yield

    # No cleanup needed - tests run in isolation
