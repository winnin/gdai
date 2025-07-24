import datetime
import uuid

import pytest
from pydantic import ValidationError

from gdai.schemas.schemas import Chunk, ChunkTypeEnum, Document, DocumentStatusEnum, DocumentTypeEnum, Query, QueryStatusEnum, ResultChunk, SimilarityTypeEnum


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
        assert isinstance(query.result_chunks, list)
        assert len(query.result_chunks) == 0

    def test_query_with_defaults(self):
        query = Query(tenant_id="tenant-1")

        assert query.query == ""
        assert query.result == ""
        assert query.status == QueryStatusEnum.pending
        assert query.similarity == SimilarityTypeEnum.cosine
        assert query.tenant_id == "tenant-1"
        assert isinstance(query.result_chunks, list)
        assert len(query.result_chunks) == 0


class TestResultChunkSchema:
    """Test suite for the ResultChunk schema."""

    @staticmethod
    def valid_result_chunk_data():
        return {
            "chunk": "This is a chunk of text from a document.",
            "type": ChunkTypeEnum.paragraph,
            "page_number": 5,
            "similarity_score": 0.92,
        }

    def test_valid_result_chunk_creation(self):
        """Test creating a valid ResultChunk instance."""
        data = self.valid_result_chunk_data()
        result_chunk = ResultChunk(**data)
        assert result_chunk.chunk == data["chunk"]
        assert result_chunk.type == ChunkTypeEnum.paragraph
        assert result_chunk.page_number == 5
        assert result_chunk.similarity_score == 0.92
        assert isinstance(result_chunk.created_at, datetime.datetime)
        assert isinstance(result_chunk.updated_at, datetime.datetime)

    def test_result_chunk_with_defaults(self):
        """Test creating a ResultChunk instance with default values."""
        result_chunk = ResultChunk(
            chunk="Default chunk",
            type=ChunkTypeEnum.paragraph,
            page_number=1,
        )
        assert result_chunk.chunk == "Default chunk"
        assert result_chunk.type == ChunkTypeEnum.paragraph
        assert result_chunk.page_number == 1
        assert result_chunk.similarity_score == 0.0  # Default value
        assert isinstance(result_chunk.created_at, datetime.datetime)
        assert isinstance(result_chunk.updated_at, datetime.datetime)

    @pytest.mark.parametrize(
        "field,value",
        [
            ("chunk", None),  # chunk can't be None
            ("type", None),  # type can't be None
            ("type", "invalid"),  # type must be valid enum
            ("page_number", None),  # page_number can't be None
            ("page_number", "not-an-int"),  # page_number must be int
            ("similarity_score", "not-a-float"),  # similarity_score must be float
        ],
    )
    def test_required_fields_and_types(self, field, value):
        """Test field requirements and type validations."""
        data = self.valid_result_chunk_data()
        data[field] = value
        with pytest.raises(ValidationError):
            ResultChunk(**data)

    def test_can_parse_datetime_strings(self):
        """Test that created_at and updated_at can parse ISO datetime strings."""
        data = self.valid_result_chunk_data()
        data["created_at"] = "2023-07-23T14:30:00Z"
        data["updated_at"] = "2023-07-23T15:45:00Z"

        result_chunk = ResultChunk(**data)
        assert result_chunk.created_at.year == 2023
        assert result_chunk.created_at.month == 7
        assert result_chunk.created_at.day == 23
        assert result_chunk.created_at.hour == 14
        assert result_chunk.created_at.minute == 30

        assert result_chunk.updated_at.year == 2023
        assert result_chunk.updated_at.month == 7
        assert result_chunk.updated_at.day == 23
        assert result_chunk.updated_at.hour == 15
        assert result_chunk.updated_at.minute == 45

    def test_similarity_score_validation(self):
        """Test that similarity_score is validated as a float between 0 and 1."""
        data = self.valid_result_chunk_data()

        # Test valid values
        valid_scores = [0.0, 0.5, 1.0]
        for score in valid_scores:
            data["similarity_score"] = score
            result_chunk = ResultChunk(**data)
            assert result_chunk.similarity_score == score
