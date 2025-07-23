import datetime
import uuid
from uuid import UUID

import pytest
from pydantic import ValidationError

from gdai.schemas.schemas import (
    Chunk,
    ChunkTypeEnum,
    Document,
    DocumentStatusEnum,
    DocumentTypeEnum,
    Query,
    QueryChunkLink,
    QueryStatusEnum,
    SimilarityTypeEnum,
)


class TestDocumentSchema:
    """Test suite for the Document schema."""

    @staticmethod
    def valid_document_data():
        return {
            "id": uuid.uuid4(),
            "tenant_id": "tenant-456",
            "name": "test_document.pdf",
            "status": DocumentStatusEnum.processed,
            "type": DocumentTypeEnum.pdf,
        }

    def test_valid_document_creation(self):
        """Test creating a valid Document instance with minimal fields."""
        data = self.valid_document_data()
        doc = Document(**data)
        assert doc.name == "test_document.pdf"
        assert doc.status == DocumentStatusEnum.processed
        assert doc.type == DocumentTypeEnum.pdf
        assert doc.id == data["id"]
        assert doc.tenant_id == "tenant-456"
        assert isinstance(doc.chunks, list)
        assert len(doc.chunks) == 0

    def test_document_with_defaults(self):
        """Test creating a Document instance with default values."""
        doc = Document(tenant_id="tenant-456")
        assert doc.name == ""
        assert doc.status == DocumentStatusEnum.uploaded
        assert doc.type == DocumentTypeEnum.pdf
        assert doc.id is None
        assert doc.tenant_id == "tenant-456"
        assert isinstance(doc.chunks, list)
        assert len(doc.chunks) == 0

    @pytest.mark.parametrize(
        "field,value,error_expected",
        [
            ("tenant_id", "", True),  # tenant_id can't be empty
            ("name", "", False),  # name can be empty (has default "")
            ("status", "invalid", True),  # invalid enum value
            ("type", "invalid", True),  # invalid enum value
        ],
    )
    def test_field_validation(self, field, value, error_expected):
        data = self.valid_document_data()
        data[field] = value
        if error_expected:
            with pytest.raises(ValidationError):
                Document(**data)
        else:
            doc = Document(**data)
            assert getattr(doc, field) == value


class TestChunkSchema:
    """Test suite for the Chunk schema."""

    @staticmethod
    def valid_chunk_data():
        return {
            "id": uuid.uuid4(),
            "tenant_id": "tenant-1",
            "document_id": uuid.uuid4(),
            "type": ChunkTypeEnum.paragraph,
            "chunk": "Content of the chunk.",
            "page_number": 1,
            "embedding": [0.1, 0.2, 0.3],
        }

    def test_valid_chunk_creation(self):
        data = self.valid_chunk_data()
        chunk = Chunk(**data)
        assert chunk.id == data["id"]
        assert chunk.tenant_id == data["tenant_id"]
        assert chunk.document_id == data["document_id"]
        assert chunk.type == ChunkTypeEnum.paragraph
        assert chunk.chunk == "Content of the chunk."
        assert chunk.page_number == 1
        assert chunk.embedding == [0.1, 0.2, 0.3]

    @pytest.mark.parametrize(
        "field,value",
        [
            ("tenant_id", ""),
            ("type", None),
        ],
    )
    def test_required_fields(self, field, value):
        data = self.valid_chunk_data()
        data[field] = value
        with pytest.raises(ValidationError):
            Chunk(**data)

    def test_embedding_can_be_none(self):
        data = self.valid_chunk_data()
        data["embedding"] = None
        chunk = Chunk(**data)
        assert chunk.embedding is None

    def test_embedding_must_be_float_list(self):
        data = self.valid_chunk_data()
        data["embedding"] = [0.1, "not-a-float", 0.3]
        with pytest.raises(ValidationError):
            Chunk(**data)


class TestQuerySchema:
    """Test suite for the Query schema."""

    @staticmethod
    def valid_query_data():
        return {
            "id": uuid.uuid4(),
            "tenant_id": "tenant-1",
            "query": "What is the meaning of life?",
            "result": "42",
            "status": QueryStatusEnum.completed,
            "similarity": SimilarityTypeEnum.cosine,
        }

    def test_valid_query_creation(self):
        data = self.valid_query_data()
        query = Query(**data)
        assert query.id == data["id"]
        assert query.tenant_id == data["tenant_id"]
        assert query.query == data["query"]
        assert query.result == data["result"]
        assert query.status == QueryStatusEnum.completed
        assert query.similarity == SimilarityTypeEnum.cosine
        assert isinstance(query.query_chunks, list)
        assert len(query.query_chunks) == 0

    def test_query_with_defaults(self):
        query = Query(tenant_id="tenant-1")
        assert query.query == ""
        assert query.result == ""
        assert query.status == QueryStatusEnum.pending
        assert query.similarity == SimilarityTypeEnum.cosine
        assert isinstance(query.id, UUID)
        assert query.tenant_id == "tenant-1"
        assert isinstance(query.query_chunks, list)
        assert len(query.query_chunks) == 0


class TestQueryChunkLinkSchema:
    """Test suite for the QueryChunkLink schema."""

    @staticmethod
    def valid_link_data():
        return {
            "query_id": uuid.uuid4(),
            "chunk_id": uuid.uuid4(),
            "similarity_score": 0.85,
        }

    def test_valid_link_creation(self):
        data = self.valid_link_data()
        link = QueryChunkLink(**data)
        assert link.query_id == data["query_id"]
        assert link.chunk_id == data["chunk_id"]
        assert link.similarity_score == 0.85
        assert isinstance(link.created_at, datetime.datetime)
        assert isinstance(link.updated_at, datetime.datetime)

    def test_link_with_defaults(self):
        data = self.valid_link_data()
        link = QueryChunkLink(**data)
        assert link.similarity_score == 0.85
        assert isinstance(link.created_at, datetime.datetime)
        assert isinstance(link.updated_at, datetime.datetime)

    @pytest.mark.parametrize(
        "field,value",
        [
            ("query_id", None),
            ("chunk_id", None),
        ],
    )
    def test_required_fields(self, field, value):
        data = self.valid_link_data()
        data[field] = value
        with pytest.raises(ValidationError):
            QueryChunkLink(**data)
