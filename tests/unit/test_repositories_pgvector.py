import asyncio
import uuid

import pytest

from src.repositories.pgvector import PGVectorDocumentRepository
from src.schemas.document import Document


@pytest.fixture(scope="module")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


class TestPGVectorDocumentRepository:
    """Test suite for the PGVectorDocumentRepository."""

    @pytest.mark.asyncio
    async def test_insert_get_and_delete_document(self):
        repo = PGVectorDocumentRepository()
        tenant_id = "test-tenant-insert"
        doc_id = str(uuid.uuid4())
        document = Document(id=doc_id, tenant_id=tenant_id, name="Documento de Teste", status="processed", type="pdf", texts=[])
        await repo.insert(tenant_id, document)
        result = await repo.get_by_id(tenant_id, doc_id)
        assert result is not None
        assert result.id == doc_id
        assert result.tenant_id == tenant_id
        assert result.name == "Documento de Teste"
        # Limpeza
        await repo.delete(tenant_id, doc_id)


# class TestPGVectorDocumentChunkRepository:
#    """Test suite for the PGVectorDocumentChunkRepository."""

# @pytest.mark.asyncio
# async def test_insert_and_get_document_chunk(self):
#     repo = PGVectorDocumentChunkRepository()
#     tenant_id = "test-tenant-chunk"
#     doc_id = str(uuid.uuid4())
#     chunk_id = str(uuid.uuid4())
#     chunk = DocumentChunk(
#         id=chunk_id,
#         tenant_id=tenant_id,
#         document_id=doc_id,
#         type="paragraph",
#         chunk="This is a test chunk.",
#         page_number=1,
#         embedding=[0.1] * 1536,  # Example embedding
#         created_at=None,
#         updated_at=None,
#     )
#     await repo.insert(tenant_id, chunk)
#     result = await repo.get_by_id(tenant_id, chunk_id)
#     assert result is not None
#     assert result.id == chunk_id
#     assert result.tenant_id == tenant_id
#     assert result.document_id == doc_id
#     assert result.chunk == "This is a test chunk."

# @pytest.mark.asyncio
# async def test_insert_get_and_delete_document_chunk():
#     repo_doc = PGVectorDocumentRepository()
#     repo_chunk = PGVectorDocumentChunkRepository()
#     tenant_id = "test-tenant-chunk"
#     doc_id = str(uuid.uuid4())
#     chunk_id = str(uuid.uuid4())

#     # Insere o documento antes do chunk
#     document = Document(id=doc_id, tenant_id=tenant_id, name="Documento para Chunk", status="processed", type="pdf", texts=[])
#     await repo_doc.insert(tenant_id, document)

#     chunk = DocumentChunk(
#         id=chunk_id,
#         tenant_id=tenant_id,
#         document_id=doc_id,
#         type="paragraph",
#         chunk="Conteúdo do chunk de teste.",
#         page_number=1,
#         embedding=[0.1] * 1536,
#         created_at=None,
#         updated_at=None,
#     )
#     await repo_chunk.insert(tenant_id, chunk)
#     result = await repo_chunk.get_by_id(tenant_id, chunk_id)
#     assert result is not None
#     assert result.id == chunk_id
#     assert result.tenant_id == tenant_id
#     assert result.document_id == doc_id
#     assert result.chunk == "Conteúdo do chunk de teste."
#     # Limpeza
#     await repo_chunk.delete(tenant_id, chunk_id)
#     await repo_doc.delete(tenant_id, doc_id)
