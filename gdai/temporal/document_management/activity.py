"""Activities for document management workflows."""

from temporalio import activity

from gdai.commons.exceptions import DocumentNotFoundError
from gdai.commons.logger import logger
from gdai.repositories import RepositoryFactory
from gdai.services.s3_storage import get_s3_storage

from .schema import (
    Chunk,
    DeleteDocumentInput,
    Document,
    DocumentStatus,
    GetDocumentChunksInput,
    GetDocumentChunksOutput,
    GetDocumentInput,
    GetDocumentStatusInput,
    ListDocumentsInput,
    ListDocumentsOutput,
)


@activity.defn
async def list_documents(input: ListDocumentsInput) -> ListDocumentsOutput:
    """List all documents for a tenant.

    Args:
        input: Input containing tenant_id

    Returns:
        ListDocumentsOutput: List of documents and total count

    Raises:
        Exception: If there's an error retrieving documents
    """
    try:
        logger.info(f"Listing documents for tenant: {input.tenant_id}")
        async with RepositoryFactory.get_repository() as repository:
            documents = await repository.get_all_documents(input.tenant_id)

        document_list = [
            Document(
                id=str(doc.id),
                name=doc.name,
                status=doc.status.value,
                type=doc.type.value,
                s3_path=doc.s3_path,
                chunk_strategy=doc.chunk_strategy,
                created_at=doc.created_at,
                updated_at=doc.updated_at,
            )
            for doc in documents
        ]

        logger.info(f"Found {len(document_list)} documents for tenant {input.tenant_id}")
        return ListDocumentsOutput(documents=document_list, total=len(document_list))

    except Exception as e:
        logger.error(f"Error listing documents for tenant {input.tenant_id}: {e}")
        raise e


@activity.defn
async def get_document(input: GetDocumentInput) -> Document:
    """Get a specific document by ID.

    Args:
        input: Input containing tenant_id and document_id

    Returns:
        Document: The requested document

    Raises:
        DocumentNotFoundError: If document is not found
        Exception: If there's an error retrieving the document
    """
    try:
        logger.info(f"Getting document {input.document_id} for tenant {input.tenant_id}")
        async with RepositoryFactory.get_repository() as repository:
            doc = await repository.get_document(input.tenant_id, input.document_id)

        if not doc:
            raise DocumentNotFoundError(input.tenant_id, input.document_id)

        document = Document(
            id=str(doc.id),
            name=doc.name,
            status=doc.status.value,
            type=doc.type.value,
            s3_path=doc.s3_path,
            chunk_strategy=doc.chunk_strategy,
            created_at=doc.created_at,
            updated_at=doc.updated_at,
        )

        logger.info(f"Found document {input.document_id} for tenant {input.tenant_id}")
        return document

    except DocumentNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error getting document {input.document_id} for tenant {input.tenant_id}: {e}")
        raise e


@activity.defn
async def delete_document(input: DeleteDocumentInput) -> bool:
    """Delete a document and all its associated chunks, including the S3 file.

    Args:
        input: Input containing tenant_id and document_id

    Returns:
        bool: True if deletion was successful

    Raises:
        DocumentNotFoundError: If document is not found
        Exception: If there's an error deleting the document
    """
    try:
        logger.info(f"Deleting document {input.document_id} for tenant {input.tenant_id}")

        async with RepositoryFactory.get_repository() as repository:
            # Check if document exists
            doc = await repository.get_document(input.tenant_id, input.document_id)
            if not doc:
                raise DocumentNotFoundError(input.tenant_id, input.document_id)

            s3_path = doc.s3_path

            # Delete chunks first
            await repository.delete_chunks(input.tenant_id, input.document_id)
            logger.info(f"Deleted chunks for document {input.document_id}")

            # Delete document from database
            deleted = await repository.delete_document(input.tenant_id, input.document_id)

            if not deleted:
                raise Exception(f"Failed to delete document {input.document_id}")

        # Delete file from S3
        s3_storage = get_s3_storage()
        try:
            s3_storage.delete_file(s3_path)
            logger.info(f"Deleted file from S3: {s3_path}")
        except Exception as e:
            logger.warning(f"Failed to delete file from S3 (document was deleted from DB): {e}")

        logger.info(f"Deleted document {input.document_id} for tenant {input.tenant_id}")
        return True

    except DocumentNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error deleting document {input.document_id} for tenant {input.tenant_id}: {e}")
        raise e


@activity.defn
async def get_document_chunks(input: GetDocumentChunksInput) -> GetDocumentChunksOutput:
    """Get all chunks for a specific document.

    Args:
        input: Input containing tenant_id and document_id

    Returns:
        GetDocumentChunksOutput: List of chunks and total count

    Raises:
        DocumentNotFoundError: If document is not found
        Exception: If there's an error retrieving chunks
    """
    try:
        logger.info(f"Getting chunks for document {input.document_id} for tenant {input.tenant_id}")
        async with RepositoryFactory.get_repository() as repository:
            # Check if document exists
            doc = await repository.get_document(input.tenant_id, input.document_id)
            if not doc:
                raise DocumentNotFoundError(input.tenant_id, input.document_id)

            # Get chunks
            chunks = await repository.get_chunks(input.tenant_id, input.document_id)

        chunk_list = [
            Chunk(
                id=str(chunk.id),
                document_id=str(chunk.document_id),
                type=chunk.type.value,
                chunk=chunk.chunk,
                page_number=chunk.page_number,
                created_at=chunk.created_at,
                updated_at=chunk.updated_at,
            )
            for chunk in chunks
        ]

        logger.info(f"Found {len(chunk_list)} chunks for document {input.document_id}")
        return GetDocumentChunksOutput(document_id=input.document_id, chunks=chunk_list, total=len(chunk_list))

    except DocumentNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error getting chunks for document {input.document_id}: {e}")
        raise e


@activity.defn
async def get_document_status(input: GetDocumentStatusInput) -> DocumentStatus:
    """Get the processing status of a document.

    Args:
        input: Input containing tenant_id and document_id

    Returns:
        DocumentStatus: Document status information

    Raises:
        DocumentNotFoundError: If document is not found
        Exception: If there's an error retrieving status
    """
    try:
        logger.info(f"Getting status for document {input.document_id} for tenant {input.tenant_id}")
        async with RepositoryFactory.get_repository() as repository:
            # Get document
            doc = await repository.get_document(input.tenant_id, input.document_id)
            if not doc:
                raise DocumentNotFoundError(input.tenant_id, input.document_id)

            # Get chunk count
            chunks = await repository.get_chunks(input.tenant_id, input.document_id)
            chunk_count = len(chunks)

        error_message = None
        if doc.status.value == "failed":
            error_message = "Processing failed"

        status = DocumentStatus(
            id=str(doc.id),
            status=doc.status.value,
            chunk_count=chunk_count,
            error_message=error_message,
        )

        logger.info(f"Document {input.document_id} status: {doc.status.value}, chunks: {chunk_count}")
        return status

    except DocumentNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error getting status for document {input.document_id}: {e}")
        raise e
