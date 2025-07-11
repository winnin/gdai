import pytest
from pydantic import ValidationError

from src.schemas.chunk import DocumentChunk


def valid_chunk_data():
    return {
        "id": "chunk-1",
        "tenant_id": "tenant-1",
        "document_id": "doc-1",
        "type": "text",
        "chunk": "Conteúdo do chunk.",
        "page_number": 1,
        "embedding": [0.1, 0.2, 0.3],
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-02T00:00:00Z",
        "begin_offset": 0,
        "end_offset": 10,
    }


def test_valid_document_chunk():
    data = valid_chunk_data()
    chunk = DocumentChunk(**data)
    assert chunk.id == data["id"]
    assert chunk.page_number == data["page_number"]


@pytest.mark.parametrize(
    "field,value",
    [
        ("id", ""),
        ("tenant_id", ""),
        ("document_id", ""),
        ("type", ""),
    ],
)
def test_empty_string_fields_raise(field, value):
    data = valid_chunk_data()
    data[field] = value
    with pytest.raises(ValidationError):
        DocumentChunk(**data)


def test_chunk_cannot_be_empty():
    data = valid_chunk_data()
    data["chunk"] = "   "
    with pytest.raises(ValidationError):
        DocumentChunk(**data)


def test_page_number_negative():
    data = valid_chunk_data()
    data["page_number"] = -1
    with pytest.raises(ValidationError):
        DocumentChunk(**data)


def test_embedding_must_be_float():
    data = valid_chunk_data()
    data["embedding"] = [0.1, "not-a-float", 0.3]
    with pytest.raises(ValidationError):
        DocumentChunk(**data)


def test_embedding_can_be_none():
    data = valid_chunk_data()
    data["embedding"] = None
    chunk = DocumentChunk(**data)
    assert chunk.embedding is None


def test_created_at_and_updated_at_can_be_none():
    data = valid_chunk_data()
    data["created_at"] = None
    data["updated_at"] = None
    chunk = DocumentChunk(**data)
    assert chunk.created_at is None
    assert chunk.updated_at is None
