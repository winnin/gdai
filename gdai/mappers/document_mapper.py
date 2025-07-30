"""Mapper for converting between Document schemas and DocumentModel ORM models."""

from gdai.commons.enums import ChunkTypeEnum, DocumentStatusEnum
from gdai.repositories.models import DocumentModel
from gdai.schemas.schemas import Chunk, Document, RawDocument


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

        return Document(
            id=model.id,
            tenant_id=model.tenant_id,
            name=model.name,
            status=model.status,
            type=model.type,
            created_at=model.created_at,
            updated_at=model.updated_at,
            chunks=[],
        )


class RawDocumentMapper:
    """Mapper for RawDocument and Document schemas."""

    @staticmethod
    def to_document(raw_document: RawDocument) -> Document:
        """Convert a RawDocument schema to a Document schema.

        Args:
            raw_document: RawDocument schema object

        Returns:
            Document: The equivalent Document schema
        """
        # Create chunks from text content
        chunks = []
        if raw_document.texts:
            for page_number, text_content in raw_document.texts:
                chunk = Chunk(
                    tenant_id=raw_document.tenant_id,
                    type=ChunkTypeEnum.paragraph,
                    chunk=text_content,
                    page_number=page_number,
                )
                chunks.append(chunk)

        # Create chunks from table content
        if raw_document.tables:
            for page_number, table_content in raw_document.tables:
                chunk = Chunk(
                    tenant_id=raw_document.tenant_id,
                    type=ChunkTypeEnum.table,
                    chunk=table_content,
                    page_number=page_number,
                )
                chunks.append(chunk)

        # Create chunks from image content (could be references or base64)
        if raw_document.images:
            for page_number, image_content in raw_document.images:
                chunk = Chunk(
                    tenant_id=raw_document.tenant_id,
                    type=ChunkTypeEnum.image,
                    chunk=image_content,  # This could be a reference to the image or base64
                    page_number=page_number,
                )
                chunks.append(chunk)

        # Create the document
        document = Document(
            tenant_id=raw_document.tenant_id,
            name=raw_document.name,
            type=raw_document.type,
            status=DocumentStatusEnum.processed,  # Set status to processed since it's been extracted
            chunks=chunks,
        )

        return document
