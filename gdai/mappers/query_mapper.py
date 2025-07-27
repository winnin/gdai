"""Mapper for converting between Query schemas and QueryModel ORM models."""

from gdai.repositories.models import QueryChunkLinkModel, QueryModel
from gdai.schemas.schemas import Query, ResultChunk


class QueryMapper:
    """Mapper for Query schema and QueryModel ORM models."""

    @staticmethod
    def to_model(query: Query) -> QueryModel:
        """Convert a Query schema to a QueryModel.

        Args:
            query: Query schema object

        Returns:
            QueryModel: The equivalent database model
        """
        query_model = QueryModel(
            id=query.id,
            tenant_id=query.tenant_id,
            query=query.query,
            result=query.result,
            status=query.status,
            similarity=query.similarity,
            created_at=query.created_at,
            updated_at=query.updated_at,
        )

        return query_model

    @staticmethod
    def to_schema(model: QueryModel) -> Query:
        """Convert a QueryModel to a Query schema.

        Args:
            model: QueryModel database object

        Returns:
            Query: The equivalent schema object
        """
        # Convert query_chunks to result_chunks for the schema
        result_chunks = []
        if model.query_chunks:
            for link in model.query_chunks:
                chunk = link.chunk
                result_chunk = ResultChunk(
                    chunk=chunk.chunk,
                    type=chunk.type,
                    page_number=chunk.page_number,
                    similarity_score=link.similarity_score,
                    created_at=link.created_at,
                    updated_at=link.updated_at,
                )
                result_chunks.append(result_chunk)

        return Query(
            id=model.id,
            tenant_id=model.tenant_id,
            query=model.query,
            result=model.result,
            status=model.status,
            similarity=model.similarity,
            created_at=model.created_at,
            updated_at=model.updated_at,
            result_chunks=result_chunks,
        )

    @staticmethod
    def create_query_chunk_link(query_model: QueryModel, chunk_model, similarity_score: float) -> QueryChunkLinkModel:
        """Create a QueryChunkLinkModel to associate a query with a chunk.

        Args:
            query_model: The QueryModel to link
            chunk_model: The ChunkModel to link
            similarity_score: The similarity score between the query and chunk

        Returns:
            QueryChunkLinkModel: The created link model
        """
        return QueryChunkLinkModel(
            query_id=query_model.id,
            chunk_id=chunk_model.id,
            similarity_score=similarity_score,
            query=query_model,
            chunk=chunk_model,
        )
