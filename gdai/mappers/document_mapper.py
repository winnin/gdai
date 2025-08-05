"""Mapper for converting between Document schemas and DocumentModel ORM models."""

from gdai.repositories.models import DocumentModel
from gdai.schemas.schemas import Document


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
            chunk_strategy=model.chunk_strategy,
            created_at=model.created_at,
            updated_at=model.updated_at,
            chunks=[],
        )
