"""Pytest configuration and shared fixtures for all tests."""

import asyncio
import os
import uuid
from collections.abc import AsyncGenerator, Generator
from pathlib import Path

import fitz  # PyMuPDF
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from gdai.commons.settings import Settings, get_settings
from gdai.repositories.models import Base
from gdai.services.s3_storage import S3StorageService


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Get test settings with proper environment configuration."""
    # Ensure test environment is loaded
    os.environ["PGVECTOR_DATABASE"] = "vectordb"  # Use same DB as docker-compose
    os.environ["S3_BUCKET"] = "gdai-test"

    # Clear the lru_cache to reload settings
    get_settings.cache_clear()

    return get_settings()


@pytest_asyncio.fixture(scope="function")
async def db_engine(test_settings):
    """Create database engine for tests."""
    engine = create_async_engine(
        test_settings.database.get_url(),
        echo=False,
        pool_pre_ping=True,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables after test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create isolated database session for each test.

    This fixture provides a clean database session for each test,
    with automatic rollback after the test completes.
    """
    from sqlalchemy.ext.asyncio import AsyncSession as SQLAlchemyAsyncSession
    from sqlalchemy.orm import sessionmaker

    # Create session factory
    async_session_maker = sessionmaker(db_engine, class_=SQLAlchemyAsyncSession, expire_on_commit=False)

    # Create session
    async with async_session_maker() as session:
        yield session
        await session.rollback()  # Rollback any uncommitted changes


@pytest_asyncio.fixture(scope="function")
async def s3_storage(test_settings) -> AsyncGenerator[S3StorageService, None]:
    """Create S3 storage service for tests with cleanup.

    This fixture provides a clean S3 environment for each test,
    cleaning up all test files after the test completes.
    """
    storage = S3StorageService()

    # Clean up any existing test files before test
    test_tenants = ["test-tenant", "tenant-1", "tenant-2", "health-check"]
    for tenant in test_tenants:
        try:
            files = storage.list_files(tenant)
            for file_key in files:
                storage.delete_file(file_key)
        except Exception:
            pass  # Ignore errors if files don't exist

    yield storage

    # Clean up test files after test
    for tenant in test_tenants:
        try:
            files = storage.list_files(tenant)
            for file_key in files:
                storage.delete_file(file_key)
        except Exception:
            pass  # Ignore cleanup errors


@pytest.fixture
def sample_tenant_id() -> str:
    """Provide a consistent test tenant ID."""
    return "test-tenant"


@pytest.fixture
def sample_document_id() -> str:
    """Provide a sample document ID for tests."""
    return str(uuid.uuid4())


@pytest.fixture
def sample_pdf_path(tmp_path: Path) -> Path:
    """Create a sample PDF document for testing.

    Creates a simple 3-page PDF with text content for testing
    document extraction and processing.
    """
    doc_path = tmp_path / "test_document.pdf"

    # Create PDF with PyMuPDF
    doc = fitz.open()
    for i in range(3):
        page = doc.new_page()
        text = f"This is page {i + 1} of the test document.\n" * 5
        page.insert_text((50, 50), text)

    doc.save(str(doc_path))
    doc.close()

    return doc_path


@pytest.fixture
def sample_large_pdf_path(tmp_path: Path) -> Path:
    """Create a larger PDF document for testing file size limits."""
    doc_path = tmp_path / "large_document.pdf"

    doc = fitz.open()
    for i in range(50):  # 50 pages
        page = doc.new_page()
        text = f"Page {i + 1}: " + ("Lorem ipsum dolor sit amet. " * 100)
        page.insert_text((50, 50), text)

    doc.save(str(doc_path))
    doc.close()

    return doc_path


@pytest.fixture
def sample_text_file(tmp_path: Path) -> Path:
    """Create a sample text file for testing."""
    file_path = tmp_path / "test.txt"
    file_path.write_text("This is a test text file.\n" * 10)
    return file_path


@pytest.fixture
def sample_empty_file(tmp_path: Path) -> Path:
    """Create an empty file for testing validation."""
    file_path = tmp_path / "empty.pdf"
    file_path.write_bytes(b"")
    return file_path


@pytest.fixture
def mock_embedding_response() -> list[list[float]]:
    """Mock Cohere API embedding response.

    Returns a list of embeddings with dimension 1536 (Cohere's dimension).
    """
    return [[0.1] * 1536 for _ in range(5)]


@pytest.fixture
def mock_llm_response() -> str:
    """Mock OpenAI API LLM response."""
    return "This is a mocked LLM response for testing purposes."


@pytest.fixture
def sample_chunks_data() -> list[dict]:
    """Sample chunk data for testing embedding and storage."""
    return [
        {
            "id": str(uuid.uuid4()),
            "tenant_id": "test-tenant",
            "document_id": str(uuid.uuid4()),
            "type": "text",
            "chunk": "First chunk of text content",
            "page_number": 1,
        },
        {
            "id": str(uuid.uuid4()),
            "tenant_id": "test-tenant",
            "document_id": str(uuid.uuid4()),
            "type": "text",
            "chunk": "Second chunk of text content",
            "page_number": 1,
        },
        {
            "id": str(uuid.uuid4()),
            "tenant_id": "test-tenant",
            "document_id": str(uuid.uuid4()),
            "type": "text",
            "chunk": "Third chunk of text content",
            "page_number": 2,
        },
    ]


# Autouse fixtures for test environment setup
@pytest.fixture(autouse=True)
def setup_test_environment(tmp_path):
    """Set up test environment for all tests.

    This fixture runs automatically for every test and ensures
    the test environment is properly configured.
    """
    # Create temp folder for extractor
    extractor_tmp = tmp_path / "extractor"
    extractor_tmp.mkdir(exist_ok=True)
    os.environ["EXTRACTOR_TMP_FOLDER"] = str(extractor_tmp)

    # Set test log level
    os.environ["GDAI_LOG_LEVEL"] = "WARNING"

    yield

    # Cleanup is handled automatically by tmp_path fixture


@pytest.fixture
def mock_temporal_env():
    """Mock Temporal environment for testing workflows.

    Note: Full Temporal integration tests should use the real
    Temporal test server. This is for unit tests only.
    """
    # TODO: Implement Temporal mocking if needed
    pass
