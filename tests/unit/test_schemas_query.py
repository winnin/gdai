import pytest
from pydantic import ValidationError

from src.schemas.query import Query, QueryDocumentChunk


class TestQueryDocumentChunk:
    def test_default_values(self):
        chunk = QueryDocumentChunk(id="c1", tenant_id="tenant1", document_id="d1", type="paragraph", page_number=1, chunk="chunk")
        assert chunk.similarity == 0.0
        assert chunk.similarity_type == "cosine"
        assert chunk.id == "c1"
        assert chunk.chunk == "chunk"
        assert chunk.document_id == "d1"

    def test_custom_similarity(self):
        chunk = QueryDocumentChunk(id="c2", tenant_id="tenant2", chunk="abc", document_id="d2", type="paragraph", page_number=1, similarity=0.75, similarity_type="dot_product")
        assert chunk.similarity == 0.75
        assert chunk.similarity_type == "dot_product"

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            QueryDocumentChunk()

    def test_invalid_similarity_type(self):
        chunk = QueryDocumentChunk(id="c3", tenant_id="tenant3", chunk="abc", document_id="d3", type="paragraph", page_number=1, similarity_type="euclidean")
        assert chunk.similarity_type == "euclidean"


class TestQuery:
    def test_valid_query(self):
        query = Query(id="id1", tenant_id="tenant1", query="busca", query_num_chunks=5, type="question&answer", chunks=[])
        assert query.tenant_id == "tenant1"
        assert query.query == "busca"
        assert query.query_num_chunks == 5
        assert query.status == "pending"
        assert isinstance(query.chunks, list)

    def test_query_min_max_length(self):
        # min_length
        with pytest.raises(ValidationError):
            Query(tenant_id="t", query="", num_chunks=1)
        # max_length
        with pytest.raises(ValidationError):
            Query(tenant_id="t", query="a" * 1001, num_chunks=1)

    def test_num_chunks_bounds(self):
        with pytest.raises(ValidationError):
            Query(tenant_id="t", query="abc", num_chunks=0)
        with pytest.raises(ValidationError):
            Query(tenant_id="t", query="abc", num_chunks=1001)

    def test_optional_fields(self):
        query = Query(
            id="q1",
            tenant_id="tenant1",
            query="busca",
            query_num_chunks=5,
            type="question&answer",
            chunks=[],
            status="done",
            result="result",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T01:00:00Z",
        )
        assert query.result == "result"
        assert query.status == "done"
        assert query.created_at == "2024-01-01T00:00:00Z"
        assert query.updated_at == "2024-01-01T01:00:00Z"
        assert query.id == "q1"
