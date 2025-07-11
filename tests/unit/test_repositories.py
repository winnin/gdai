"""Tests for the pgvector repository module."""

from __future__ import annotations

import asyncio
import uuid

import pytest
import pytest_asyncio

from src.config.database import PGVectorDatabase
from src.repositories.pgvector import PGVectorDocumentRepository
from src.schemas.chunk import DocumentChunk
from src.schemas.document import Document

# Constants for testing
TEST_TENANT_ID = "test_tenant_pgvector"


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_connection():
    """Get a database connection for testing."""
    async with PGVectorDatabase.get_connection() as conn:
        yield conn


@pytest_asyncio.fixture(scope="function")
async def clean_tenant():
    """Clean up the tenant data before and after tests."""
    # Clean before test
    repo = PGVectorDocumentRepository()
    await repo.clean_tenant_database(TEST_TENANT_ID)
    yield
    # Clean after test
    await repo.clean_tenant_database(TEST_TENANT_ID)


@pytest_asyncio.fixture(scope="function")
async def sample_document():
    """Create a sample document for testing."""
    doc_id = str(uuid.uuid4())
    doc = Document(
        id=doc_id,
        tenant_id=TEST_TENANT_ID,
        name="test_document.pdf",
        status="processed",
        type="pdf",
    )
    return doc


@pytest_asyncio.fixture(scope="function")
async def sample_chunks(sample_document):
    """Create sample document chunks for testing."""
    chunks = []
    for i in range(3):
        chunk_id = str(uuid.uuid4())
        chunk = DocumentChunk(
            id=chunk_id,
            tenant_id=TEST_TENANT_ID,
            chunk_type="paragraph",
            chunk=f"Sample text {i} for document {sample_document.id}",
            page_number=i,
            embedding=[0.1, 0.2, 0.3] * 512,  # 1536 dimensions
            document_id=sample_document.id,
        )
        chunks.append(chunk)
    return chunks


@pytest_asyncio.fixture(scope="function")
async def inserted_document(_, sample_document, sample_chunks):
    """Insert a document with chunks into the database."""
    repo = PGVectorDocumentRepository()
    await repo.create(TEST_TENANT_ID, sample_document, sample_chunks)
    yield (sample_document, sample_chunks)
    # Cleanup is handled by clean_tenant fixture


@pytest.mark.asyncio
class TestDocumentRepository:
    """Test suite for DocumentRepository."""

    async def test_get_all_documents_by_tenant_id(self, inserted_document):
        """Test retrieving all documents for a tenant."""
        doc, _ = inserted_document
        repo = PGVectorDocumentRepository()

        # Get all documents
        documents = await repo.get_all_documents_by_tenant_id(TEST_TENANT_ID)

        # Verify we get at least the document we inserted
        assert len(documents) >= 1
        assert any(d.id == doc.id for d in documents)
        assert all(d.tenant_id == TEST_TENANT_ID for d in documents)

    async def test_get_by_id(self, inserted_document):
        """Test retrieving a document by ID."""
        doc, _ = inserted_document
        repo = PGVectorDocumentRepository()

        # Get the document
        retrieved_doc = await repo.get_by_id(TEST_TENANT_ID, doc.id)

        # Verify document properties
        assert retrieved_doc is not None
        assert retrieved_doc.id == doc.id
        assert retrieved_doc.tenant_id == TEST_TENANT_ID
        assert retrieved_doc.name == doc.name
        assert retrieved_doc.type == doc.type

        # Test with non-existent ID
        non_existent_doc = await repo.get_by_id(TEST_TENANT_ID, "non-existent-id")
        assert non_existent_doc is None

    async def test_get_document_chunk_by_id(self, inserted_document):
        """Test retrieving a document chunk by ID."""
        _, chunks = inserted_document
        repo = PGVectorDocumentRepository()

        # Get a chunk
        chunk = chunks[0]
        retrieved_chunk = await repo.get_document_chunk_by_id(TEST_TENANT_ID, chunk.chunk_id)

        # Verify chunk properties
        assert retrieved_chunk is not None
        assert retrieved_chunk.id == chunk.chunk_id
        assert retrieved_chunk.tenant_id == TEST_TENANT_ID
        assert retrieved_chunk.chunk == chunk.chunk_text
        assert retrieved_chunk.page_number == chunk.page_number

        # Test with non-existent ID
        non_existent_chunk = await repo.get_document_chunk_by_id(TEST_TENANT_ID, "non-existent-id")
        assert non_existent_chunk is None

    async def test_insert_document(self, _, sample_document, sample_chunks):
        """Test inserting a document and chunks."""
        repo = PGVectorDocumentRepository()

        # Insert document and chunks
        await repo.create(TEST_TENANT_ID, sample_document, sample_chunks)

        # Verify document was inserted
        doc = await repo.get_by_id(TEST_TENANT_ID, sample_document.id)
        assert doc is not None
        assert doc.id == sample_document.id

        # Verify chunks were inserted
        for chunk in sample_chunks:
            retrieved_chunk = await repo.get_document_chunk_by_id(TEST_TENANT_ID, chunk.chunk_id)
            assert retrieved_chunk is not None
            assert retrieved_chunk.id == chunk.chunk_id

    async def test_delete_document(self, _, sample_document, sample_chunks):
        """Test deleting a document."""
        repo = PGVectorDocumentRepository()

        # Insert document and chunks first
        await repo.create(TEST_TENANT_ID, sample_document, sample_chunks)

        # Verify document exists
        retrieved_doc = await repo.get_by_id(TEST_TENANT_ID, sample_document.id)
        assert retrieved_doc is not None

        # Delete document
        await repo.delete(TEST_TENANT_ID, sample_document.id)

        # Verify document was deleted
        deleted_doc = await repo.get_by_id(TEST_TENANT_ID, sample_document.id)
        assert deleted_doc is None

        # Verify chunks were deleted
        for chunk in sample_chunks:
            deleted_chunk = await repo.get_document_chunk_by_id(TEST_TENANT_ID, chunk.chunk_id)
            assert deleted_chunk is None

    async def test_clean_tenant_database(self, _):
        """Test cleaning all documents for a tenant."""
        repo = PGVectorDocumentRepository()

        # Create multiple documents
        doc1 = Document(
            id=str(uuid.uuid4()),
            tenant_id=TEST_TENANT_ID,
            name="test_doc1.pdf",
            status="processed",
            type="pdf",
        )

        doc2 = Document(
            id=str(uuid.uuid4()),
            tenant_id=TEST_TENANT_ID,
            name="test_doc2.pdf",
            status="processed",
            type="pdf",
        )

        chunk1 = DocumentChunk(
            id=str(uuid.uuid4()),
            tenant_id=TEST_TENANT_ID,
            chunk_type="paragraph",
            chunk="Content for doc1",
            page_number=1,
            embedding=[0.1, 0.2, 0.3] * 512,
            document_id=doc1.id,
        )

        chunk2 = DocumentChunk(
            id=str(uuid.uuid4()),
            tenant_id=TEST_TENANT_ID,
            chunk_type="paragraph",
            chunk="Content for doc2",
            page_number=1,
            embedding=[0.4, 0.5, 0.6] * 512,
            document_id=doc2.id,
        )

        # Insert documents
        await repo.create(TEST_TENANT_ID, doc1, [chunk1])
        await repo.create(TEST_TENANT_ID, doc2, [chunk2])

        # Verify documents exist
        docs = await repo.get_all_documents_by_tenant_id(TEST_TENANT_ID)
        assert len(docs) == 2

        # Clean tenant database
        await repo.clean_tenant_database(TEST_TENANT_ID)

        # Verify all documents were deleted
        docs = await repo.get_all_documents_by_tenant_id(TEST_TENANT_ID)
        assert len(docs) == 0

        # Verify specific documents were deleted
        deleted_doc1 = await repo.get_by_id(TEST_TENANT_ID, doc1.id)
        deleted_doc2 = await repo.get_by_id(TEST_TENANT_ID, doc2.id)
        assert deleted_doc1 is None
        assert deleted_doc2 is None

        # Verify chunks were deleted
        deleted_chunk1 = await repo.get_document_chunk_by_id(TEST_TENANT_ID, chunk1.id)
        deleted_chunk2 = await repo.get_document_chunk_by_id(TEST_TENANT_ID, chunk2.id)
        assert deleted_chunk1 is None
        assert deleted_chunk2 is None
