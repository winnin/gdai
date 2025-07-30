"""Integration tests for the PgVector repository."""

import uuid
from datetime import datetime

import pytest

from gdai.commons.enums import ChunkTypeEnum, DocumentStatusEnum, DocumentTypeEnum
from gdai.repositories.pgvector_repository import PGVectorRepository
from gdai.schemas.schemas import Document


class TestPgVectorRepository:
    """Test suite for the PgVectorRepository."""

    @staticmethod
    def valid_document_data():
        """Return valid document data for testing."""
        return {
            "id": uuid.uuid4(),
            "tenant_id": "test-tenant",
            "name": "test_document.pdf",
            "status": DocumentStatusEnum.uploaded,
            "type": DocumentTypeEnum.pdf,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "chunks": [
                {
                    "id": uuid.uuid4(),
                    "tenant_id": "test-tenant",
                    "type": ChunkTypeEnum.paragraph,
                    "chunk": "This is the first chunk of the document.",
                    "page_number": 1,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now(),
                },
                {
                    "id": uuid.uuid4(),
                    "tenant_id": "test-tenant",
                    "type": ChunkTypeEnum.paragraph,
                    "chunk": "This is the second chunk of the document.",
                    "page_number": 2,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now(),
                },
            ],
        }

    @pytest.mark.asyncio
    async def test_insert_document_and_chunks(self):
        repository = PGVectorRepository()
        document_data = self.valid_document_data()
        document = Document(**document_data)
        result = await repository.insert_document_and_chunks(document)
        assert result is not None
        assert result.tenant_id == document.tenant_id
        # cleaning up the inserted document
        await repository.delete_document_and_chunks(document.id)
