"""Unit tests for PGVectorRepository."""

import uuid

import pytest

from gdai.commons.enums import ChunkTypeEnum, DocumentStatusEnum, DocumentTypeEnum
from gdai.repositories.models import ChunkModel, DocumentModel
from gdai.repositories.pgvector_repository import PGVectorRepository


class TestPGVectorRepository:
    """Test suite for PGVectorRepository."""

    @pytest.mark.asyncio
    async def test_insert_document(self, db_session, sample_tenant_id):
        """Test document insertion."""
        repo = PGVectorRepository(db_session)

        doc_id = uuid.uuid4()
        doc = DocumentModel(
            id=doc_id,
            tenant_id=sample_tenant_id,
            name="test.pdf",
            type=DocumentTypeEnum.pdf,
            s3_path=f"{sample_tenant_id}/test.pdf",
            status=DocumentStatusEnum.processed,
            chunk_strategy="semantic",
        )

        result = await repo.insert_document(doc)

        assert result.id == doc_id
        assert result.name == "test.pdf"
        assert result.s3_path == f"{sample_tenant_id}/test.pdf"
        assert result.status == DocumentStatusEnum.processed
        assert result.tenant_id == sample_tenant_id

    @pytest.mark.asyncio
    async def test_get_document_exists(self, db_session, sample_tenant_id):
        """Test retrieving an existing document."""
        repo = PGVectorRepository(db_session)

        # Insert document
        doc_id = uuid.uuid4()
        doc = DocumentModel(
            id=doc_id,
            tenant_id=sample_tenant_id,
            name="test.pdf",
            type=DocumentTypeEnum.pdf,
            s3_path=f"{sample_tenant_id}/test.pdf",
        )
        await repo.insert_document(doc)

        # Retrieve
        retrieved = await repo.get_document(sample_tenant_id, str(doc_id))

        assert retrieved is not None
        assert retrieved.id == doc_id
        assert retrieved.name == "test.pdf"
        assert retrieved.tenant_id == sample_tenant_id

    @pytest.mark.asyncio
    async def test_get_document_not_found(self, db_session, sample_tenant_id):
        """Test retrieving a nonexistent document."""
        repo = PGVectorRepository(db_session)

        result = await repo.get_document(sample_tenant_id, str(uuid.uuid4()))

        assert result is None

    @pytest.mark.asyncio
    async def test_get_document_wrong_tenant(self, db_session):
        """Test that documents are isolated by tenant."""
        repo = PGVectorRepository(db_session)

        # Insert document for tenant-1
        doc_id = uuid.uuid4()
        doc = DocumentModel(
            id=doc_id,
            tenant_id="tenant-1",
            name="test.pdf",
            type=DocumentTypeEnum.pdf,
            s3_path="tenant-1/test.pdf",
        )
        await repo.insert_document(doc)

        # Try to retrieve with tenant-2
        result = await repo.get_document("tenant-2", str(doc_id))

        assert result is None  # Should not find document from another tenant

    @pytest.mark.asyncio
    async def test_get_all_documents(self, db_session, sample_tenant_id):
        """Test listing all documents for a tenant."""
        repo = PGVectorRepository(db_session)

        # Insert multiple documents
        for i in range(3):
            doc = DocumentModel(
                id=uuid.uuid4(),
                tenant_id=sample_tenant_id,
                name=f"doc{i}.pdf",
                type=DocumentTypeEnum.pdf,
                s3_path=f"{sample_tenant_id}/doc{i}.pdf",
            )
            await repo.insert_document(doc)

        # Retrieve all
        docs = await repo.get_all_documents(sample_tenant_id)

        assert len(docs) == 3
        assert all(d.tenant_id == sample_tenant_id for d in docs)
        assert {d.name for d in docs} == {"doc0.pdf", "doc1.pdf", "doc2.pdf"}

    @pytest.mark.asyncio
    async def test_get_all_documents_empty(self, db_session):
        """Test listing documents for tenant with no documents."""
        repo = PGVectorRepository(db_session)

        docs = await repo.get_all_documents("empty-tenant")

        assert docs == []

    @pytest.mark.asyncio
    async def test_delete_document(self, db_session, sample_tenant_id):
        """Test document deletion."""
        repo = PGVectorRepository(db_session)

        # Insert document
        doc_id = uuid.uuid4()
        doc = DocumentModel(
            id=doc_id,
            tenant_id=sample_tenant_id,
            name="test.pdf",
            type=DocumentTypeEnum.pdf,
            s3_path=f"{sample_tenant_id}/test.pdf",
        )
        await repo.insert_document(doc)

        # Delete
        deleted = await repo.delete_document(sample_tenant_id, str(doc_id))

        assert deleted is True

        # Verify deleted
        retrieved = await repo.get_document(sample_tenant_id, str(doc_id))
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_document(self, db_session, sample_tenant_id):
        """Test deleting a document that doesn't exist."""
        repo = PGVectorRepository(db_session)

        deleted = await repo.delete_document(sample_tenant_id, str(uuid.uuid4()))

        assert deleted is False

    @pytest.mark.asyncio
    async def test_insert_chunks(self, db_session, sample_tenant_id):
        """Test inserting multiple chunks."""
        repo = PGVectorRepository(db_session)

        # Create document first
        doc_id = uuid.uuid4()
        doc = DocumentModel(
            id=doc_id,
            tenant_id=sample_tenant_id,
            name="test.pdf",
            type=DocumentTypeEnum.pdf,
            s3_path=f"{sample_tenant_id}/test.pdf",
        )
        await repo.insert_document(doc)

        # Create chunks
        chunks = [
            ChunkModel(
                id=uuid.uuid4(),
                tenant_id=sample_tenant_id,
                document_id=doc_id,
                type=ChunkTypeEnum.text,
                chunk=f"Chunk {i} content",
                page_number=i + 1,
                embedding=[0.1] * 1536,  # Mock embedding
            )
            for i in range(3)
        ]

        # Insert chunks
        await repo.insert_batch_chunks(chunks)

        # Verify
        retrieved_chunks = await repo.get_chunks(sample_tenant_id, str(doc_id))
        assert len(retrieved_chunks) == 3

    @pytest.mark.asyncio
    async def test_get_chunks(self, db_session, sample_tenant_id):
        """Test retrieving chunks for a document."""
        repo = PGVectorRepository(db_session)

        # Create document
        doc_id = uuid.uuid4()
        doc = DocumentModel(
            id=doc_id,
            tenant_id=sample_tenant_id,
            name="test.pdf",
            type=DocumentTypeEnum.pdf,
            s3_path=f"{sample_tenant_id}/test.pdf",
        )
        await repo.insert_document(doc)

        # Create and insert chunks
        chunks = [
            ChunkModel(
                id=uuid.uuid4(),
                tenant_id=sample_tenant_id,
                document_id=doc_id,
                type=ChunkTypeEnum.text,
                chunk=f"Content {i}",
                page_number=i,
                embedding=[0.1] * 1536,
            )
            for i in range(5)
        ]
        await repo.insert_batch_chunks(chunks)

        # Retrieve
        retrieved = await repo.get_chunks(sample_tenant_id, str(doc_id))

        assert len(retrieved) == 5
        assert all(c.document_id == doc_id for c in retrieved)
        assert all(c.tenant_id == sample_tenant_id for c in retrieved)

    @pytest.mark.asyncio
    async def test_delete_chunks(self, db_session, sample_tenant_id):
        """Test deleting all chunks for a document."""
        repo = PGVectorRepository(db_session)

        # Create document and chunks
        doc_id = uuid.uuid4()
        doc = DocumentModel(
            id=doc_id,
            tenant_id=sample_tenant_id,
            name="test.pdf",
            type=DocumentTypeEnum.pdf,
            s3_path=f"{sample_tenant_id}/test.pdf",
        )
        await repo.insert_document(doc)

        chunks = [
            ChunkModel(
                id=uuid.uuid4(),
                tenant_id=sample_tenant_id,
                document_id=doc_id,
                type=ChunkTypeEnum.text,
                chunk=f"Chunk {i}",
                page_number=i,
                embedding=[0.1] * 1536,
            )
            for i in range(3)
        ]
        await repo.insert_batch_chunks(chunks)

        # Delete chunks
        await repo.delete_chunks(sample_tenant_id, str(doc_id))

        # Verify chunks deleted
        remaining = await repo.get_chunks(sample_tenant_id, str(doc_id))
        assert len(remaining) == 0

    @pytest.mark.asyncio
    async def test_tenant_isolation_documents(self, db_session):
        """Test that documents are properly isolated by tenant."""
        repo = PGVectorRepository(db_session)

        # Insert documents for different tenants
        tenant1_doc = DocumentModel(
            id=uuid.uuid4(),
            tenant_id="tenant-1",
            name="doc1.pdf",
            type=DocumentTypeEnum.pdf,
            s3_path="tenant-1/doc1.pdf",
        )
        tenant2_doc = DocumentModel(
            id=uuid.uuid4(),
            tenant_id="tenant-2",
            name="doc2.pdf",
            type=DocumentTypeEnum.pdf,
            s3_path="tenant-2/doc2.pdf",
        )

        await repo.insert_document(tenant1_doc)
        await repo.insert_document(tenant2_doc)

        # Verify isolation
        tenant1_docs = await repo.get_all_documents("tenant-1")
        tenant2_docs = await repo.get_all_documents("tenant-2")

        assert len(tenant1_docs) == 1
        assert len(tenant2_docs) == 1
        assert tenant1_docs[0].tenant_id == "tenant-1"
        assert tenant2_docs[0].tenant_id == "tenant-2"

    @pytest.mark.asyncio
    async def test_tenant_isolation_chunks(self, db_session):
        """Test that chunks are properly isolated by tenant."""
        repo = PGVectorRepository(db_session)

        # Create documents for different tenants
        doc1_id = uuid.uuid4()
        doc2_id = uuid.uuid4()

        doc1 = DocumentModel(
            id=doc1_id,
            tenant_id="tenant-1",
            name="doc1.pdf",
            type=DocumentTypeEnum.pdf,
            s3_path="tenant-1/doc1.pdf",
        )
        doc2 = DocumentModel(
            id=doc2_id,
            tenant_id="tenant-2",
            name="doc2.pdf",
            type=DocumentTypeEnum.pdf,
            s3_path="tenant-2/doc2.pdf",
        )

        await repo.insert_document(doc1)
        await repo.insert_document(doc2)

        # Add chunks
        chunk1 = ChunkModel(
            id=uuid.uuid4(),
            tenant_id="tenant-1",
            document_id=doc1_id,
            type=ChunkTypeEnum.text,
            chunk="Tenant 1 content",
            page_number=1,
            embedding=[0.1] * 1536,
        )
        chunk2 = ChunkModel(
            id=uuid.uuid4(),
            tenant_id="tenant-2",
            document_id=doc2_id,
            type=ChunkTypeEnum.text,
            chunk="Tenant 2 content",
            page_number=1,
            embedding=[0.2] * 1536,
        )

        await repo.insert_batch_chunks([chunk1])
        await repo.insert_batch_chunks([chunk2])

        # Verify isolation
        tenant1_chunks = await repo.get_chunks("tenant-1", str(doc1_id))
        tenant2_chunks = await repo.get_chunks("tenant-2", str(doc2_id))

        assert len(tenant1_chunks) == 1
        assert len(tenant2_chunks) == 1
        assert tenant1_chunks[0].chunk == "Tenant 1 content"
        assert tenant2_chunks[0].chunk == "Tenant 2 content"

        # Tenant 1 cannot access tenant 2's chunks
        tenant1_accessing_doc2 = await repo.get_chunks("tenant-1", str(doc2_id))
        assert len(tenant1_accessing_doc2) == 0

    @pytest.mark.asyncio
    async def test_context_manager_usage(self, test_settings, sample_tenant_id):
        """Test repository usage as context manager."""
        # Use repository as context manager
        async with PGVectorRepository() as repo:
            doc = DocumentModel(
                id=uuid.uuid4(),
                tenant_id=sample_tenant_id,
                name="context_test.pdf",
                type=DocumentTypeEnum.pdf,
                s3_path=f"{sample_tenant_id}/context_test.pdf",
            )

            result = await repo.insert_document(doc)
            assert result.name == "context_test.pdf"

        # Session should be closed after context exit

    @pytest.mark.asyncio
    async def test_document_with_all_fields(self, db_session, sample_tenant_id):
        """Test document with all optional fields populated."""
        repo = PGVectorRepository(db_session)

        doc_id = uuid.uuid4()
        doc = DocumentModel(
            id=doc_id,
            tenant_id=sample_tenant_id,
            name="complete.pdf",
            type=DocumentTypeEnum.pdf,
            s3_path=f"{sample_tenant_id}/complete.pdf",
            status=DocumentStatusEnum.processed,
            chunk_strategy="semantic-window-512",
        )

        result = await repo.insert_document(doc)

        assert result.id == doc_id
        assert result.status == DocumentStatusEnum.processed
        assert result.chunk_strategy == "semantic-window-512"

        # Verify retrieval
        retrieved = await repo.get_document(sample_tenant_id, str(doc_id))
        assert retrieved.chunk_strategy == "semantic-window-512"
