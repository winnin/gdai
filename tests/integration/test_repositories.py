from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import numpy as np
import pytest
import pytest_asyncio

from gdai.commons.config import Config
from gdai.commons.enums import ChunkTypeEnum, DocumentTypeEnum, QueryStatusEnum
from gdai.repositories.models import ChunkModel, DocumentModel, QueryModel
from gdai.repositories.pgvector_repository import PGVectorRepository

# Configure pytest-asyncio to use the same event loop for all tests
pytest_plugins = ("pytest_asyncio",)


@pytest_asyncio.fixture
def repository():
    """Create repository instance.

    Note: This assumes the database has been set up using scripts/setup_db.py
    """
    try:
        # Verify database configuration is available
        _ = Config.db.PGVECTOR_USER
        _ = Config.db.PGVECTOR_PASSWORD
        _ = Config.db.PGVECTOR_DATABASE
    except Exception as e:
        pytest.skip(f"Database configuration not available: {e}")

    return PGVectorRepository()


@pytest_asyncio.fixture
def tenant_id():
    """Generate unique tenant ID for each test."""
    return str(uuid4())


class TestPGVectorRepositoryDocuments:
    """Test document CRUD operations."""

    @pytest.mark.asyncio
    async def test_insert_and_get_document(self, repository, tenant_id):
        """Test inserting a document and retrieving it."""
        doc_id = uuid4()
        document = DocumentModel(
            id=doc_id,
            name="test_document.pdf",
            tenant_id=tenant_id,
            type=DocumentTypeEnum.pdf,
            chunk_strategy="recursive",
        )

        # Insert document
        await repository.insert_document(document)

        # Retrieve document
        retrieved_document = await repository.get_document(tenant_id, str(doc_id))

        assert retrieved_document is not None
        assert str(retrieved_document.id) == str(doc_id)
        assert retrieved_document.tenant_id == tenant_id
        assert retrieved_document.name == "test_document.pdf"
        assert retrieved_document.type == DocumentTypeEnum.pdf

    @pytest.mark.asyncio
    async def test_get_all_documents(self, repository, tenant_id):
        """Test retrieving all documents for a tenant."""
        # Insert multiple documents
        doc_ids = [uuid4() for _ in range(3)]
        for idx, doc_id in enumerate(doc_ids):
            document = DocumentModel(
                id=doc_id,
                name=f"document_{idx}.pdf",
                tenant_id=tenant_id,
                type=DocumentTypeEnum.pdf,
                chunk_strategy="recursive",
            )
            await repository.insert_document(document)

        # Retrieve all documents
        documents = await repository.get_all_documents(tenant_id)

        assert len(documents) == 3
        retrieved_ids = {str(doc.id) for doc in documents}
        assert retrieved_ids == {str(doc_id) for doc_id in doc_ids}

    @pytest.mark.asyncio
    async def test_delete_document(self, repository, tenant_id):
        """Test deleting a document."""
        doc_id = uuid4()
        document = DocumentModel(
            id=doc_id,
            name="document_to_delete.pdf",
            tenant_id=tenant_id,
            type=DocumentTypeEnum.pdf,
            chunk_strategy="recursive",
        )
        await repository.insert_document(document)

        # Delete document
        await repository.delete_document(tenant_id, str(doc_id))

        # Verify deletion - get_document raises ValueError when not found
        try:
            await repository.get_document(tenant_id, str(doc_id))
            assert False, "Expected ValueError for deleted document"
        except ValueError as e:
            assert "not found" in str(e)

    @pytest.mark.asyncio
    async def test_get_document_nonexistent(self, repository, tenant_id):
        """Test retrieving a nonexistent document raises ValueError."""
        doc_id = str(uuid4())
        try:
            await repository.get_document(tenant_id, doc_id)
            assert False, "Expected ValueError for nonexistent document"
        except ValueError as e:
            assert "not found" in str(e)

    @pytest.mark.asyncio
    async def test_tenant_isolation_documents(self, repository):
        """Test that documents are isolated by tenant."""
        tenant1 = str(uuid4())
        tenant2 = str(uuid4())
        doc_id = uuid4()

        # Insert document for tenant1
        document = DocumentModel(
            id=doc_id, name="tenant1_doc.pdf", tenant_id=tenant1, type=DocumentTypeEnum.pdf, chunk_strategy="recursive"
        )
        await repository.insert_document(document)

        # Tenant2 should not see the document
        try:
            await repository.get_document(tenant2, str(doc_id))
            assert False, "Expected ValueError when accessing other tenant's document"
        except ValueError as e:
            assert "not found" in str(e)

        # Tenant1 should see the document
        retrieved_document = await repository.get_document(tenant1, str(doc_id))
        assert retrieved_document is not None

    @pytest.mark.asyncio
    async def test_document_timestamps(self, repository, tenant_id):
        """Test that document timestamps are set correctly."""
        doc_id = uuid4()
        before = datetime.now(UTC)

        document = DocumentModel(
            id=doc_id,
            name="timestamp_doc.pdf",
            tenant_id=tenant_id,
            type=DocumentTypeEnum.pdf,
            chunk_strategy="recursive",
        )
        await repository.insert_document(document)

        after = datetime.now(UTC)
        retrieved_document = await repository.get_document(tenant_id, str(doc_id))

        assert retrieved_document.created_at is not None
        assert retrieved_document.updated_at is not None
        assert before <= retrieved_document.created_at.replace(tzinfo=UTC) <= after
        assert before <= retrieved_document.updated_at.replace(tzinfo=UTC) <= after


class TestPGVectorRepositoryChunks:
    """Test chunk operations."""

    @pytest.mark.asyncio
    async def test_insert_chunks(self, repository, tenant_id):
        """Test inserting chunks for a document."""
        doc_id = uuid4()
        document = DocumentModel(
            id=doc_id,
            name="doc_with_chunks.pdf",
            tenant_id=tenant_id,
            type=DocumentTypeEnum.pdf,
            chunk_strategy="recursive",
        )
        await repository.insert_document(document)

        # Insert chunks
        chunk_id1 = uuid4()
        chunk_id2 = uuid4()
        chunks = [
            ChunkModel(
                id=chunk_id1,
                tenant_id=tenant_id,
                document_id=doc_id,
                type=ChunkTypeEnum.text,
                chunk="Chunk 1",
                page_number=1,
            ),
            ChunkModel(
                id=chunk_id2,
                tenant_id=tenant_id,
                document_id=doc_id,
                type=ChunkTypeEnum.text,
                chunk="Chunk 2",
                page_number=2,
            ),
        ]
        await repository.insert_chunks(chunks)

        # Verify chunks
        retrieved_chunks = await repository.get_chunks(tenant_id, str(doc_id))
        assert len(retrieved_chunks) == 2
        assert retrieved_chunks[0].chunk == "Chunk 1"
        assert retrieved_chunks[1].chunk == "Chunk 2"

    @pytest.mark.asyncio
    async def test_insert_batch_chunks(self, repository, tenant_id):
        """Test batch inserting chunks."""
        doc_id = uuid4()
        document = DocumentModel(
            id=doc_id,
            name="batch_chunks_doc.pdf",
            tenant_id=tenant_id,
            type=DocumentTypeEnum.pdf,
            chunk_strategy="recursive",
        )
        await repository.insert_document(document)

        # Create 10 chunks
        chunks = [
            ChunkModel(
                id=uuid4(),
                tenant_id=tenant_id,
                document_id=doc_id,
                type=ChunkTypeEnum.text,
                chunk=f"Chunk {i}",
                page_number=i,
            )
            for i in range(10)
        ]
        await repository.insert_batch_chunks(chunks)

        # Verify all chunks inserted
        retrieved_chunks = await repository.get_chunks(tenant_id, str(doc_id))
        assert len(retrieved_chunks) == 10

    @pytest.mark.asyncio
    async def test_get_chunks_without_embedding(self, repository, tenant_id):
        """Test retrieving chunks without embeddings."""
        doc_id = uuid4()
        document = DocumentModel(
            id=doc_id,
            name="no_embedding_doc.pdf",
            tenant_id=tenant_id,
            type=DocumentTypeEnum.pdf,
            chunk_strategy="recursive",
        )
        await repository.insert_document(document)

        # Insert chunks without embeddings
        chunk_id1 = uuid4()
        chunk_id2 = uuid4()
        chunks = [
            ChunkModel(
                id=chunk_id1,
                tenant_id=tenant_id,
                document_id=doc_id,
                type=ChunkTypeEnum.text,
                chunk="Chunk 1",
                page_number=1,
            ),
            ChunkModel(
                id=chunk_id2,
                tenant_id=tenant_id,
                document_id=doc_id,
                type=ChunkTypeEnum.text,
                chunk="Chunk 2",
                page_number=2,
            ),
        ]
        await repository.insert_chunks(chunks)

        # Get chunks without embedding
        chunks_without_embedding = await repository.get_chunks_without_embedding(batch_size=20)
        assert len(chunks_without_embedding) >= 2
        for chunk in chunks_without_embedding:
            if str(chunk.document_id) == str(doc_id):
                assert chunk.embedding is None

    @pytest.mark.asyncio
    async def test_update_chunks_with_embeddings(self, repository, tenant_id):
        """Test updating chunks with embeddings."""
        doc_id = uuid4()
        document = DocumentModel(
            id=doc_id,
            name="embedding_update_doc.pdf",
            tenant_id=tenant_id,
            type=DocumentTypeEnum.pdf,
            chunk_strategy="recursive",
        )
        await repository.insert_document(document)

        chunk_id = uuid4()
        chunk = ChunkModel(
            id=chunk_id,
            tenant_id=tenant_id,
            document_id=doc_id,
            type=ChunkTypeEnum.text,
            chunk="Test chunk",
            page_number=1,
        )
        await repository.insert_chunks([chunk])

        # Update with embedding
        embedding = np.random.rand(1536).tolist()
        chunk_with_embedding = ChunkModel(
            id=chunk_id,
            tenant_id=tenant_id,
            document_id=doc_id,
            type=ChunkTypeEnum.text,
            chunk="Test chunk",
            page_number=1,
            embedding=embedding,
        )
        await repository.update_chunks([chunk_with_embedding])

        # Verify embedding was set
        retrieved_chunks = await repository.get_chunks(tenant_id, str(doc_id))
        assert retrieved_chunks[0].embedding is not None
        assert len(retrieved_chunks[0].embedding) == 1536

    @pytest.mark.asyncio
    async def test_delete_chunks(self, repository, tenant_id):
        """Test deleting chunks."""
        doc_id = uuid4()
        document = DocumentModel(
            id=doc_id,
            name="delete_chunks_doc.pdf",
            tenant_id=tenant_id,
            type=DocumentTypeEnum.pdf,
            chunk_strategy="recursive",
        )
        await repository.insert_document(document)

        chunks = [
            ChunkModel(
                id=uuid4(),
                tenant_id=tenant_id,
                document_id=doc_id,
                type=ChunkTypeEnum.text,
                chunk="Chunk 1",
                page_number=1,
            ),
            ChunkModel(
                id=uuid4(),
                tenant_id=tenant_id,
                document_id=doc_id,
                type=ChunkTypeEnum.text,
                chunk="Chunk 2",
                page_number=2,
            ),
        ]
        await repository.insert_chunks(chunks)

        # Delete chunks
        await repository.delete_chunks(tenant_id, str(doc_id))

        # Verify deletion
        retrieved_chunks = await repository.get_chunks(tenant_id, str(doc_id))
        assert len(retrieved_chunks) == 0

    @pytest.mark.asyncio
    async def test_tenant_isolation_chunks(self, repository):
        """Test that chunks are isolated by tenant."""
        tenant1 = str(uuid4())
        tenant2 = str(uuid4())
        doc_id = uuid4()

        # Insert document and chunks for tenant1
        document = DocumentModel(
            id=doc_id,
            name="tenant1_chunks_doc.pdf",
            tenant_id=tenant1,
            type=DocumentTypeEnum.pdf,
            chunk_strategy="recursive",
        )
        await repository.insert_document(document)

        chunk = ChunkModel(
            id=uuid4(), tenant_id=tenant1, document_id=doc_id, type=ChunkTypeEnum.text, chunk="Chunk 1", page_number=1
        )
        await repository.insert_chunks([chunk])

        # Tenant2 should not see the chunks
        chunks = await repository.get_chunks(tenant2, str(doc_id))
        assert len(chunks) == 0

        # Tenant1 should see the chunks
        chunks = await repository.get_chunks(tenant1, str(doc_id))
        assert len(chunks) == 1

    @pytest.mark.asyncio
    async def test_chunk_cascade_delete(self, repository, tenant_id):
        """Test that chunks are deleted when document is deleted."""
        doc_id = uuid4()
        document = DocumentModel(
            id=doc_id,
            name="cascade_delete_doc.pdf",
            tenant_id=tenant_id,
            type=DocumentTypeEnum.pdf,
            chunk_strategy="recursive",
        )
        await repository.insert_document(document)

        chunk = ChunkModel(
            id=uuid4(), tenant_id=tenant_id, document_id=doc_id, type=ChunkTypeEnum.text, chunk="Chunk 1", page_number=1
        )
        await repository.insert_chunks([chunk])

        # Delete document
        await repository.delete_document(tenant_id, str(doc_id))

        # Chunks should be deleted
        chunks = await repository.get_chunks(tenant_id, str(doc_id))
        assert len(chunks) == 0


class TestPGVectorRepositoryVectorSearch:
    """Test vector similarity search operations."""

    @pytest.mark.asyncio
    async def test_search_chunks_by_similarity(self, repository, tenant_id):
        """Test searching chunks by vector similarity."""
        doc_id = uuid4()
        document = DocumentModel(
            id=doc_id,
            name="similarity_search_doc.pdf",
            tenant_id=tenant_id,
            type=DocumentTypeEnum.pdf,
            chunk_strategy="recursive",
        )
        await repository.insert_document(document)

        # Create chunks with embeddings
        chunk_id1 = uuid4()
        chunk_id2 = uuid4()
        chunk_id3 = uuid4()

        # Insert chunks without embeddings first
        chunks = [
            ChunkModel(
                id=chunk_id1,
                tenant_id=tenant_id,
                document_id=doc_id,
                type=ChunkTypeEnum.text,
                chunk="Machine learning is great",
                page_number=1,
            ),
            ChunkModel(
                id=chunk_id2,
                tenant_id=tenant_id,
                document_id=doc_id,
                type=ChunkTypeEnum.text,
                chunk="Deep learning is powerful",
                page_number=2,
            ),
            ChunkModel(
                id=chunk_id3,
                tenant_id=tenant_id,
                document_id=doc_id,
                type=ChunkTypeEnum.text,
                chunk="The weather is sunny",
                page_number=3,
            ),
        ]
        await repository.insert_chunks(chunks)

        # Add embeddings (simulating similar vectors for ML-related content)
        base_embedding = np.random.rand(1536)
        chunks_with_embeddings = [
            ChunkModel(
                id=chunk_id1,
                tenant_id=tenant_id,
                document_id=doc_id,
                type=ChunkTypeEnum.text,
                chunk="Machine learning is great",
                page_number=1,
                embedding=base_embedding.tolist(),
            ),
            ChunkModel(
                id=chunk_id2,
                tenant_id=tenant_id,
                document_id=doc_id,
                type=ChunkTypeEnum.text,
                chunk="Deep learning is powerful",
                page_number=2,
                embedding=(base_embedding + 0.1 * np.random.rand(1536)).tolist(),
            ),
            ChunkModel(
                id=chunk_id3,
                tenant_id=tenant_id,
                document_id=doc_id,
                type=ChunkTypeEnum.text,
                chunk="The weather is sunny",
                page_number=3,
                embedding=np.random.rand(1536).tolist(),
            ),
        ]
        await repository.update_chunks(chunks_with_embeddings)

        # Search with query similar to first embedding
        query_embedding = (base_embedding + 0.05 * np.random.rand(1536)).tolist()
        results = await repository.search_chunks_by_similarity_on_document_ids(
            tenant_id=tenant_id, document_ids=[str(doc_id)], query_embedding=query_embedding, limit=2
        )

        assert len(results) == 2
        # Results should be ordered by similarity
        assert results[0].chunk in ["Machine learning is great", "Deep learning is powerful"]

    @pytest.mark.asyncio
    async def test_search_multiple_documents(self, repository, tenant_id):
        """Test searching across multiple documents."""
        doc_id1 = uuid4()
        doc_id2 = uuid4()

        # Create two documents
        document1 = DocumentModel(
            id=doc_id1,
            name="multi_doc1.pdf",
            tenant_id=tenant_id,
            type=DocumentTypeEnum.pdf,
            chunk_strategy="recursive",
        )
        document2 = DocumentModel(
            id=doc_id2,
            name="multi_doc2.pdf",
            tenant_id=tenant_id,
            type=DocumentTypeEnum.pdf,
            chunk_strategy="recursive",
        )
        await repository.insert_document(document1)
        await repository.insert_document(document2)

        # Add chunks to both documents
        chunk1_id = uuid4()
        chunk2_id = uuid4()

        chunks = [
            ChunkModel(
                id=chunk1_id,
                tenant_id=tenant_id,
                document_id=doc_id1,
                type=ChunkTypeEnum.text,
                chunk="Content 1",
                page_number=1,
            ),
            ChunkModel(
                id=chunk2_id,
                tenant_id=tenant_id,
                document_id=doc_id2,
                type=ChunkTypeEnum.text,
                chunk="Content 2",
                page_number=1,
            ),
        ]
        await repository.insert_chunks(chunks)

        # Add embeddings
        embedding1 = np.random.rand(1536).tolist()
        embedding2 = np.random.rand(1536).tolist()

        chunks_with_embeddings = [
            ChunkModel(
                id=chunk1_id,
                tenant_id=tenant_id,
                document_id=doc_id1,
                type=ChunkTypeEnum.text,
                chunk="Content 1",
                page_number=1,
                embedding=embedding1,
            ),
            ChunkModel(
                id=chunk2_id,
                tenant_id=tenant_id,
                document_id=doc_id2,
                type=ChunkTypeEnum.text,
                chunk="Content 2",
                page_number=1,
                embedding=embedding2,
            ),
        ]
        await repository.update_chunks(chunks_with_embeddings)

        # Search across both documents
        query_embedding = np.random.rand(1536).tolist()
        results = await repository.search_chunks_by_similarity_on_document_ids(
            tenant_id=tenant_id, document_ids=[str(doc_id1), str(doc_id2)], query_embedding=query_embedding, limit=10
        )

        assert len(results) == 2


class TestPGVectorRepositoryQueries:
    """Test query operations."""

    @pytest.mark.asyncio
    async def test_insert_and_get_query(self, repository, tenant_id):
        """Test inserting and retrieving a query."""
        query_id = uuid4()
        query_text = "What is machine learning?"

        query = QueryModel(id=query_id, tenant_id=tenant_id, query=query_text, status=QueryStatusEnum.pending)
        await repository.insert_query(query)

        retrieved_query = await repository.get_query(tenant_id, str(query_id))

        assert retrieved_query is not None
        assert str(retrieved_query.id) == str(query_id)
        assert retrieved_query.query == query_text
        assert retrieved_query.result == ""

    @pytest.mark.asyncio
    async def test_update_query_result(self, repository, tenant_id):
        """Test updating query result."""
        query_id = uuid4()
        query = QueryModel(id=query_id, tenant_id=tenant_id, query="What is AI?", status=QueryStatusEnum.pending)
        await repository.insert_query(query)

        result = "Artificial Intelligence is the simulation of human intelligence."
        await repository.update_query_result(
            query_id=str(query_id), tenant_id=tenant_id, result=result, status="completed"
        )

        retrieved_query = await repository.get_query(tenant_id, str(query_id))
        assert retrieved_query.result == result

    @pytest.mark.asyncio
    async def test_insert_query_chunk_links(self, repository, tenant_id):
        """Test inserting query-chunk links."""
        # Setup document and chunk
        doc_id = uuid4()
        chunk_id = uuid4()

        document = DocumentModel(
            id=doc_id,
            name="link_test_doc.pdf",
            tenant_id=tenant_id,
            type=DocumentTypeEnum.pdf,
            chunk_strategy="recursive",
        )
        await repository.insert_document(document)

        chunk = ChunkModel(
            id=chunk_id,
            tenant_id=tenant_id,
            document_id=doc_id,
            type=ChunkTypeEnum.text,
            chunk="Test content",
            page_number=1,
        )
        await repository.insert_chunks([chunk])

        # Setup query
        query_id = uuid4()
        query = QueryModel(id=query_id, tenant_id=tenant_id, query="Test query", status=QueryStatusEnum.pending)
        await repository.insert_query(query)

        # Insert link
        links = [(str(chunk_id), 0.95)]
        await repository.insert_query_chunk_links(
            tenant_id=tenant_id, query_id=str(query_id), chunks_ids_with_similarity=links
        )

        # Verify link exists (implicitly through successful insert)
        retrieved_query = await repository.get_query(tenant_id, str(query_id))
        assert retrieved_query is not None

    @pytest.mark.asyncio
    async def test_query_timestamps(self, repository, tenant_id):
        """Test that query timestamps are set correctly."""
        query_id = uuid4()
        before = datetime.now(UTC)

        query = QueryModel(id=query_id, tenant_id=tenant_id, query="Test query", status=QueryStatusEnum.pending)
        await repository.insert_query(query)

        after = datetime.now(UTC)
        retrieved_query = await repository.get_query(tenant_id, str(query_id))

        assert retrieved_query.created_at is not None
        assert retrieved_query.updated_at is not None
        assert before <= retrieved_query.created_at.replace(tzinfo=UTC) <= after


class TestPGVectorRepositoryIntegration:
    """Test end-to-end workflows."""

    @pytest.mark.asyncio
    async def test_complete_rag_workflow(self, repository, tenant_id):
        """Test complete RAG workflow: document -> chunks -> embeddings -> search -> query."""
        # 1. Insert document
        doc_id = uuid4()
        document = DocumentModel(
            id=doc_id,
            name="rag_workflow_doc.pdf",
            tenant_id=tenant_id,
            type=DocumentTypeEnum.pdf,
            chunk_strategy="recursive",
        )
        await repository.insert_document(document)

        # 2. Insert chunks
        chunk_id1 = uuid4()
        chunk_id2 = uuid4()
        chunk_id3 = uuid4()

        chunks = [
            ChunkModel(
                id=chunk_id1,
                tenant_id=tenant_id,
                document_id=doc_id,
                type=ChunkTypeEnum.text,
                chunk="Python is a programming language",
                page_number=1,
            ),
            ChunkModel(
                id=chunk_id2,
                tenant_id=tenant_id,
                document_id=doc_id,
                type=ChunkTypeEnum.text,
                chunk="Java is also a programming language",
                page_number=2,
            ),
            ChunkModel(
                id=chunk_id3,
                tenant_id=tenant_id,
                document_id=doc_id,
                type=ChunkTypeEnum.text,
                chunk="Cats are animals",
                page_number=3,
            ),
        ]
        await repository.insert_chunks(chunks)

        # 3. Add embeddings
        base_embedding = np.random.rand(1536)
        chunks_with_embeddings = [
            ChunkModel(
                id=chunk_id1,
                tenant_id=tenant_id,
                document_id=doc_id,
                type=ChunkTypeEnum.text,
                chunk="Python is a programming language",
                page_number=1,
                embedding=base_embedding.tolist(),
            ),
            ChunkModel(
                id=chunk_id2,
                tenant_id=tenant_id,
                document_id=doc_id,
                type=ChunkTypeEnum.text,
                chunk="Java is also a programming language",
                page_number=2,
                embedding=(base_embedding + 0.1 * np.random.rand(1536)).tolist(),
            ),
            ChunkModel(
                id=chunk_id3,
                tenant_id=tenant_id,
                document_id=doc_id,
                type=ChunkTypeEnum.text,
                chunk="Cats are animals",
                page_number=3,
                embedding=np.random.rand(1536).tolist(),
            ),
        ]
        await repository.update_chunks(chunks_with_embeddings)

        # 4. Search for relevant chunks
        query_embedding = (base_embedding + 0.05 * np.random.rand(1536)).tolist()
        search_results = await repository.search_chunks_by_similarity_on_document_ids(
            tenant_id=tenant_id, document_ids=[str(doc_id)], query_embedding=query_embedding, limit=2
        )

        assert len(search_results) == 2

        # 5. Create query
        query_id = uuid4()
        query = QueryModel(id=query_id, tenant_id=tenant_id, query="What is Python?", status=QueryStatusEnum.pending)
        await repository.insert_query(query)

        # 6. Link chunks to query
        links = [(str(chunk.id), 0.9) for chunk in search_results]
        await repository.insert_query_chunk_links(
            tenant_id=tenant_id, query_id=str(query_id), chunks_ids_with_similarity=links
        )

        # 7. Update query result
        result = "Python is a programming language used for various applications."
        await repository.update_query_result(
            query_id=str(query_id), tenant_id=tenant_id, result=result, status="completed"
        )

        # Verify final state
        final_query = await repository.get_query(tenant_id, str(query_id))
        assert final_query.result == result

    @pytest.mark.asyncio
    async def test_multi_tenant_isolation(self, repository):
        """Test complete isolation between tenants."""
        tenant1 = str(uuid4())
        tenant2 = str(uuid4())

        # Tenant 1 creates document
        doc1_id = uuid4()
        document1 = DocumentModel(
            id=doc1_id, name="tenant1_doc.pdf", tenant_id=tenant1, type=DocumentTypeEnum.pdf, chunk_strategy="recursive"
        )
        await repository.insert_document(document1)

        chunk1_id = uuid4()
        chunk1 = ChunkModel(
            id=chunk1_id,
            tenant_id=tenant1,
            document_id=doc1_id,
            type=ChunkTypeEnum.text,
            chunk="Tenant 1 content",
            page_number=1,
        )
        await repository.insert_chunks([chunk1])

        # Tenant 2 creates document
        doc2_id = uuid4()
        document2 = DocumentModel(
            id=doc2_id, name="tenant2_doc.pdf", tenant_id=tenant2, type=DocumentTypeEnum.pdf, chunk_strategy="recursive"
        )
        await repository.insert_document(document2)

        chunk2_id = uuid4()
        chunk2 = ChunkModel(
            id=chunk2_id,
            tenant_id=tenant2,
            document_id=doc2_id,
            type=ChunkTypeEnum.text,
            chunk="Tenant 2 content",
            page_number=1,
        )
        await repository.insert_chunks([chunk2])

        # Verify isolation
        tenant1_docs = await repository.get_all_documents(tenant1)
        tenant2_docs = await repository.get_all_documents(tenant2)

        assert len(tenant1_docs) == 1
        assert len(tenant2_docs) == 1
        assert str(tenant1_docs[0].id) == str(doc1_id)
        assert str(tenant2_docs[0].id) == str(doc2_id)

        # Verify chunk isolation
        tenant1_chunks = await repository.get_chunks(tenant1, str(doc1_id))
        tenant2_chunks = await repository.get_chunks(tenant2, str(doc2_id))

        assert len(tenant1_chunks) == 1
        assert len(tenant2_chunks) == 1
        assert tenant1_chunks[0].chunk == "Tenant 1 content"
        assert tenant2_chunks[0].chunk == "Tenant 2 content"

    @pytest.mark.asyncio
    async def test_document_lifecycle(self, repository, tenant_id):
        """Test complete document lifecycle from creation to deletion."""
        doc_id = uuid4()

        # Create document
        document = DocumentModel(
            id=doc_id,
            name="lifecycle_doc.pdf",
            tenant_id=tenant_id,
            type=DocumentTypeEnum.pdf,
            chunk_strategy="recursive",
        )
        await repository.insert_document(document)

        # Add chunks
        chunk_ids = [uuid4() for _ in range(5)]
        chunks = [
            ChunkModel(
                id=cid,
                tenant_id=tenant_id,
                document_id=doc_id,
                type=ChunkTypeEnum.text,
                chunk=f"Content {i}",
                page_number=i,
            )
            for i, cid in enumerate(chunk_ids)
        ]
        await repository.insert_chunks(chunks)

        # Add embeddings
        chunks_with_embeddings = [
            ChunkModel(
                id=cid,
                tenant_id=tenant_id,
                document_id=doc_id,
                type=ChunkTypeEnum.text,
                chunk=f"Content {i}",
                page_number=i,
                embedding=np.random.rand(1536).tolist(),
            )
            for i, cid in enumerate(chunk_ids)
        ]
        await repository.update_chunks(chunks_with_embeddings)

        # Verify chunks with embeddings
        retrieved_chunks = await repository.get_chunks(tenant_id, str(doc_id))
        assert len(retrieved_chunks) == 5
        for chunk in retrieved_chunks:
            assert chunk.embedding is not None

        # Delete specific chunks
        await repository.delete_chunks(tenant_id, str(doc_id))
        retrieved_chunks = await repository.get_chunks(tenant_id, str(doc_id))
        assert len(retrieved_chunks) == 0

        # Document should still exist
        retrieved_document = await repository.get_document(tenant_id, str(doc_id))
        assert retrieved_document is not None

        # Delete document
        await repository.delete_document(tenant_id, str(doc_id))
        try:
            await repository.get_document(tenant_id, str(doc_id))
            assert False, "Expected ValueError for deleted document"
        except ValueError as e:
            assert "not found" in str(e)
