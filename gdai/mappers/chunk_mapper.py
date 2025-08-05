from gdai.commons.enums import ChunkTypeEnum
from gdai.repositories.models import ChunkModel
from gdai.schemas.schemas import Chunk, RawDocument


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
