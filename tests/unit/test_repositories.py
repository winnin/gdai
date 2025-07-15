import asyncio
import uuid

import pytest

from src.repositories.pgvector import PGVectorDocumentRepository
from src.schemas.chunk import DocumentChunk
from src.schemas.document import Document


@pytest.fixture(scope="module")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def test_data():
    """Create test data for two different tenants."""
    tenant_ids = ["test-tenant-1", "test-tenant-2"]
    documents = []
    chunks = []

    # Create 5 test documents for each tenant
    for tenant_id in tenant_ids:
        for i in range(5):
            doc_id = str(uuid.uuid4())
            document = Document(
                id=doc_id,
                tenant_id=tenant_id,
                name=f"Test Document {i+1} for {tenant_id}",
                status="processed",
                type="pdf",
                texts=[],  # Not used in repository tests
            )
            documents.append(document)

            # Create 2 chunks for each document
            for j in range(2):
                chunk_id = str(uuid.uuid4())
                chunk = DocumentChunk(
                    id=chunk_id,
                    tenant_id=tenant_id,
                    type="paragraph",
                    chunk=f"Test chunk {j+1} for document {i+1} in tenant {tenant_id}",
                    page_number=j,
                    embedding=[0.1] * 1536,  # 1536-dimensional vector
                    document_id=doc_id,
                )
                chunks.append(chunk)

    # Insert test data into database
    repo = PGVectorDocumentRepository()

    for doc, chunk_group in zip(documents, [chunks[i : i + 2] for i in range(0, len(chunks), 2)]):
        await repo.create(doc.tenant_id, doc, chunk_group)

    yield {"tenant_ids": tenant_ids, "documents": documents, "chunks": chunks}

    # Clean up test data
    for tenant_id in tenant_ids:
        await repo.clean_tenant_database(tenant_id)


class TestPGVectorDocumentRepository:
    """Tests for the PGVectorDocumentRepository implementation."""

    @pytest.mark.asyncio
    async def test_get_all_documents_by_tenant_id(self, test_data):
        """Test getting all documents for a specific tenant."""
        repo = PGVectorDocumentRepository()
        tenant_id = test_data["tenant_ids"][0]

        documents = await repo.get_all_documents_by_tenant_id(tenant_id)
        import pdb

        pdb.set_trace()
        assert len(documents) == 5
        for doc in documents:
            assert isinstance(doc, Document)
            assert doc.tenant_id == tenant_id

    # @pytest.mark.asyncio
    # async def test_get_all_documents_by_tenant_id_invalid(self):
    #     """Test getting all documents for a non-existent tenant."""
    #     repo = PGVectorDocumentRepository()
    #     documents = await repo.get_all_documents_by_tenant_id("non-existent-tenant")

    #     assert len(documents) == 0

    # @pytest.mark.asyncio
    # async def test_get_by_id(self, test_data):
    #     """Test getting a document by ID."""
    #     repo = PGVectorDocumentRepository()
    #     doc = test_data["documents"][0]
    #     tenant_id = doc.tenant_id
    #     doc_id = doc.id

    #     retrieved_doc = await repo.get_by_id(tenant_id, doc_id)

    #     assert retrieved_doc is not None
    #     assert retrieved_doc.id == doc_id
    #     assert retrieved_doc.tenant_id == tenant_id
    #     assert retrieved_doc.name == doc.name
    #     assert retrieved_doc.type == doc.type

    # @pytest.mark.asyncio
    # async def test_get_by_id_invalid(self, test_data):
    #     """Test getting a document with invalid ID."""
    #     repo = PGVectorDocumentRepository()
    #     tenant_id = test_data["tenant_ids"][0]

    #     # Test with non-existent document ID
    #     result = await repo.get_by_id(tenant_id, str(uuid.uuid4()))
    #     assert result is None

    #     # Test with invalid tenant ID for existing document
    #     doc = test_data["documents"][0]
    #     result = await repo.get_by_id("wrong-tenant", doc.id)
    #     assert result is None

    # @pytest.mark.asyncio
    # async def test_get_document_chunk_by_id(self, test_data):
    #     """Test getting a document chunk by ID."""
    #     repo = PGVectorDocumentRepository()
    #     chunk = test_data["chunks"][0]
    #     tenant_id = chunk.tenant_id
    #     chunk_id = chunk.id

    #     retrieved_chunk = await repo.get_document_chunk_by_id(tenant_id, chunk_id)

    #     assert retrieved_chunk is not None
    #     assert retrieved_chunk.id == chunk_id
    #     assert retrieved_chunk.tenant_id == tenant_id
    #     assert retrieved_chunk.chunk_type == chunk.chunk_type
    #     assert retrieved_chunk.chunk == chunk.chunk
    #     assert retrieved_chunk.page_number == chunk.page_number
    #     assert retrieved_chunk.document_id == chunk.document_id

    # @pytest.mark.asyncio
    # async def test_get_document_chunk_by_id_invalid(self, test_data):
    #     """Test getting a chunk with invalid ID."""
    #     repo = PGVectorDocumentRepository()
    #     tenant_id = test_data["tenant_ids"][0]

    #     # Test with non-existent chunk ID
    #     result = await repo.get_document_chunk_by_id(tenant_id, str(uuid.uuid4()))
    #     assert result is None

    #     # Test with invalid tenant ID for existing chunk
    #     chunk = test_data["chunks"][0]
    #     result = await repo.get_document_chunk_by_id("wrong-tenant", chunk.id)
    #     assert result is None

    # @pytest.mark.asyncio
    # async def test_create(self):
    #     """Test creating a new document with chunks."""
    #     repo = PGVectorDocumentRepository()
    #     tenant_id = "test-create-tenant"
    #     doc_id = str(uuid.uuid4())

    #     # Create test document
    #     document = Document(id=doc_id, tenant_id=tenant_id, name="Test Create Document", status="processed", type="pdf", texts=[])

    #     # Create test chunks
    #     chunks = []
    #     for i in range(2):
    #         chunk = DocumentChunk(
    #             id=str(uuid.uuid4()), tenant_id=tenant_id, chunk_type="paragraph", chunk=f"Test create chunk {i+1}", page_number=i, embedding=[0.2] * 1536, document_id=doc_id
    #         )
    #         chunks.append(chunk)

    #     # Create document and chunks
    #     await repo.create(tenant_id, document, chunks)

    #     # Verify document was created
    #     retrieved_doc = await repo.get_by_id(tenant_id, doc_id)
    #     assert retrieved_doc is not None
    #     assert retrieved_doc.id == doc_id
    #     assert retrieved_doc.tenant_id == tenant_id

    #     # Clean up
    #     await repo.clean_tenant_database(tenant_id)

    # @pytest.mark.asyncio
    # async def test_create_invalid(self):
    #     """Test creating a document with invalid data."""
    #     repo = PGVectorDocumentRepository()
    #     tenant_id = "test-invalid-tenant"
    #     doc_id = str(uuid.uuid4())

    #     # Create document with valid data
    #     document = Document(id=doc_id, tenant_id=tenant_id, name="Test Invalid Document", status="processed", type="pdf", texts=[])

    #     # Create chunk with invalid data (too large embedding)
    #     chunk = DocumentChunk(
    #         id=str(uuid.uuid4()),
    #         tenant_id=tenant_id,
    #         chunk_type="paragraph",
    #         chunk="Test invalid chunk",
    #         page_number=0,
    #         embedding=[0.1] * 2000,  # Too large for pgvector's 1536 dimensions
    #         document_id=doc_id,
    #     )

    #     # Attempt to create with invalid data
    #     with pytest.raises(Exception):
    #         await repo.create(tenant_id, document, [chunk])

    #     # Verify nothing was created
    #     result = await repo.get_by_id(tenant_id, doc_id)
    #     assert result is None

    # @pytest.mark.asyncio
    # async def test_delete(self, test_data):
    #     """Test deleting a document."""
    #     repo = PGVectorDocumentRepository()
    #     doc = test_data["documents"][9]  # Use the last test document
    #     tenant_id = doc.tenant_id
    #     doc_id = doc.id

    #     # Verify document exists
    #     retrieved_doc = await repo.get_by_id(tenant_id, doc_id)
    #     assert retrieved_doc is not None

    #     # Delete the document
    #     await repo.delete(tenant_id, doc_id)

    #     # Verify document was deleted
    #     deleted_doc = await repo.get_by_id(tenant_id, doc_id)
    #     assert deleted_doc is None

    # @pytest.mark.asyncio
    # async def test_delete_invalid(self):
    #     """Test deleting a document with invalid ID."""
    #     repo = PGVectorDocumentRepository()

    #     # This should not raise an exception even with invalid data
    #     await repo.delete("non-existent-tenant", str(uuid.uuid4()))

    # @pytest.mark.asyncio
    # async def test_delete_many(self):
    #     """Test delete_many method (currently a no-op)."""
    #     repo = PGVectorDocumentRepository()
    #     # This should not raise an exception
    #     await repo.delete_many("test-tenant", {})

    # @pytest.mark.asyncio
    # async def test_clean_tenant_database(self):
    #     """Test cleaning all data for a tenant."""
    #     repo = PGVectorDocumentRepository()
    #     tenant_id = "test-clean-tenant"

    #     # Create test document and chunks
    #     doc_id = str(uuid.uuid4())
    #     document = Document(id=doc_id, tenant_id=tenant_id, name="Test Clean Document", status="processed", type="pdf", texts=[])

    #     chunk = DocumentChunk(
    #         id=str(uuid.uuid4()), tenant_id=tenant_id, chunk_type="paragraph", chunk="Test clean chunk", page_number=0, embedding=[0.3] * 1536, document_id=doc_id
    #     )

    #     # Insert test data
    #     await repo.create(tenant_id, document, [chunk])

    #     # Verify data was created
    #     docs = await repo.get_all_documents_by_tenant_id(tenant_id)
    #     assert len(docs) == 1

    #     # Clean the tenant database
    #     await repo.clean_tenant_database(tenant_id)

    #     # Verify all data was removed
    #     docs_after = await repo.get_all_documents_by_tenant_id(tenant_id)
    #     assert len(docs_after) == 0

    # @pytest.mark.asyncio
    # async def test_read(self):
    #     """Test read method (currently a no-op)."""
    #     repo = PGVectorDocumentRepository()
    #     # This should not raise an exception
    #     await repo.read("test-tenant")

    # @pytest.mark.asyncio
    # async def test_update(self):
    #     """Test update method (currently a no-op)."""
    #     repo = PGVectorDocumentRepository()
    #     # This should not raise an exception
    #     await repo.update("test-tenant")
