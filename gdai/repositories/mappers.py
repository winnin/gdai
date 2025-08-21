from gdai.commons.enums import ChunkTypeEnum
from gdai.repositories.models import ChunkModel, DocumentModel, QueryChunkLinkModel, QueryModel
from gdai.schemas.schemas import Chunk, Document, Query, RawDocument, ResultChunk


class ChunkMapper:
    """Mapper for Chunk schema and ChunkModel ORM models."""

    @staticmethod
    def to_model(chunk: Chunk, document_model=None) -> ChunkModel:
        """Convert a Chunk schema to a ChunkModel.

        Args:
            chunk: Chunk schema object
            document_model: Optional parent DocumentModel

        Returns:
            ChunkModel: The equivalent database model
        """
        chunk_model = ChunkModel(
            tenant_id=chunk.tenant_id,
            type=chunk.type,
            chunk=chunk.chunk,
            page_number=chunk.page_number,
            embedding=chunk.embedding,
        )

        if document_model:
            chunk_model.document = document_model

        return chunk_model

    @staticmethod
    def to_schema(model: ChunkModel) -> Chunk:
        """Convert a ChunkModel to a Chunk schema.

        Args:
            model: ChunkModel database object

        Returns:
            Chunk: The equivalent schema object
        """
        return Chunk(
            id=model.id,
            tenant_id=model.tenant_id,
            type=model.type,
            chunk=model.chunk,
            page_number=model.page_number,
            embedding=model.embedding,
            document_id=model.document_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class RawChunkerMapper:
    """Mapper for RawDocument and Document schemas."""

    @staticmethod
    def to_chunks(raw_document: RawDocument) -> list[Chunk]:
        """Convert a RawDocument schema to a list of Chunk Schemas.

        Args:
            raw_document: RawDocument schema object

        Returns:
            list[Chunk]: The equivalent list of Chunk schemas
        """
        chunks = []
        if raw_document.texts:
            for page_number, text_content in raw_document.texts:
                chunk = Chunk(
                    tenant_id=raw_document.tenant_id,
                    type=ChunkTypeEnum.text,
                    chunk=text_content,
                    page_number=page_number,
                )
                chunks.append(chunk)

        if raw_document.tables:
            for page_number, table_content in raw_document.tables:
                chunk = Chunk(
                    tenant_id=raw_document.tenant_id,
                    type=ChunkTypeEnum.table,
                    chunk=table_content,
                    page_number=page_number,
                )
                chunks.append(chunk)

        if raw_document.images:
            for page_number, image_content in raw_document.images:
                chunk = Chunk(
                    tenant_id=raw_document.tenant_id,
                    type=ChunkTypeEnum.image,
                    chunk=image_content,
                    page_number=page_number,
                )
                chunks.append(chunk)

        return chunks


class DocumentMapper:
    """Mapper for Document schema and DocumentModel ORM models."""

    @staticmethod
    def to_model(document: Document) -> DocumentModel:
        """Convert a Document schema to a DocumentModel.

        Args:
            document: Document schema object

        Returns:
            DocumentModel: The equivalent database model
        """

        document_model = DocumentModel(
            tenant_id=document.tenant_id,
            name=document.name,
            status=document.status,
            type=document.type,
            chunk_strategy=document.chunk_strategy,
            retry_extraction=document.retry_extraction,
            retry_embedding=document.retry_embedding,
            created_at=document.created_at,
            updated_at=document.updated_at,
        )

        return document_model

    @staticmethod
    def to_schema(model: DocumentModel) -> Document:
        """Convert a DocumentModel to a Document schema.

        Args:
            model: DocumentModel database object

        Returns:
            Document: The equivalent schema object
        """

        doc = Document(
            id=model.id,
            tenant_id=model.tenant_id,
            name=model.name,
            status=model.status,
            type=model.type,
            chunk_strategy=model.chunk_strategy,
            retry_extraction=model.retry_extraction,
            retry_embedding=model.retry_embedding,
            created_at=model.created_at,
            updated_at=model.updated_at,
            chunks=[],
        )

        return doc


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

        return Query(
            id=model.id,
            tenant_id=model.tenant_id,
            query=model.query,
            result=model.result,
            status=model.status,
            similarity=model.similarity,
            created_at=model.created_at,
            updated_at=model.updated_at,
            result_chunks=[],
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


class ResultChunkMapper:
    """Mapper for Chunk schema and ChunkModel ORM models."""

    @staticmethod
    def to_schema(chunk_model: ChunkModel, similarity: float) -> ResultChunk:
        """Convert a ChunkModel to a Chunk schema.

        Args:
            model: ChunkModel database object

        Returns:
            Chunk: The equivalent schema object
        """
        result = ResultChunk(
            chunk=chunk_model.chunk,
            document_id=str(chunk_model.document_id),
            type=chunk_model.type,
            similarity_score=similarity,
            page_number=chunk_model.page_number,
        )
        return result
