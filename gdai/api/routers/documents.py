"""Document management endpoints."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Path, UploadFile, status
from temporalio.client import Client

from gdai.api.dependencies import get_current_tenant, get_repository, get_temporal_client
from gdai.commons.enums import DocumentStatusEnum, DocumentTypeEnum
from gdai.commons.exceptions import DocumentNotFoundError, FileUploadError
from gdai.commons.logger import logger
from gdai.domain.chunk import ChunkDTO, ChunkListResponse
from gdai.domain.document import DocumentDTO, DocumentListResponse, DocumentStatusDTO
from gdai.repositories.models import DocumentModel
from gdai.repositories.pgvector_repository import PGVectorRepository
from gdai.temporal.extract_document.schema import DocumentExtracInput
from gdai.temporal.extract_document.workflow import DocumentExtractionWorkflow

router = APIRouter()


@router.post(
    "/documents",
    response_model=DocumentDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a new document",
    description="Upload a document for processing. The document will be saved and queued for extraction.",
    tags=["documents"],
)
async def upload_document(
    file: UploadFile = File(..., description="Document file to upload"),
    document_type: DocumentTypeEnum = Form(..., description="Type of the document (pdf, etc)"),
    chunk_strategy: str = Form("recursive", description="Chunking strategy to use"),
    tenant_id: Annotated[str, Depends(get_current_tenant)] = None,
    repository: Annotated[PGVectorRepository, Depends(get_repository)] = None,
    temporal_client: Annotated[Client, Depends(get_temporal_client)] = None,
) -> DocumentDTO:
    """Upload a new document for processing.

    Args:
        file: The document file to upload.
        document_type: Type of the document.
        chunk_strategy: Chunking strategy to apply.
        tenant_id: Tenant identifier from header.
        repository: Database repository instance.

    Returns:
        DocumentDTO: Created document information.

    Raises:
        HTTPException: If file upload or document creation fails.
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No filename provided")

        # Save file to /tmp for now
        # TODO: Implement proper file storage (S3, etc.)
        file_path = f"/tmp/{uuid.uuid4()}_{file.filename}"

        try:
            contents = await file.read()
            with open(file_path, "wb") as f:
                f.write(contents)
        except Exception as e:
            raise FileUploadError(file.filename, str(e))

        # Create document record
        document = DocumentModel(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            name=file.filename,
            type=document_type,
            status=DocumentStatusEnum.processed,  # Will be updated by workflow
            chunk_strategy=chunk_strategy,
        )

        # Save to database with "processing" status
        document.status = DocumentStatusEnum.processing
        document = await repository.insert_document(document)

        # Trigger Temporal workflow for document processing
        try:
            workflow_id = f"extract-doc-{document.id}"
            await temporal_client.start_workflow(
                DocumentExtractionWorkflow.run,
                DocumentExtracInput(document_path=file_path, chunk_strategy=chunk_strategy, tenant_id=tenant_id),
                id=workflow_id,
                task_queue="document-processing",
            )
            logger.info(f"Started document extraction workflow {workflow_id} for document {document.id}")
        except Exception as e:
            logger.error(f"Failed to start workflow for document {document.id}: {e}")
            # Don't fail the request - workflow can be retried
            # Document status will remain "processing" and can be checked later

        return DocumentDTO.model_validate(document)

    except FileUploadError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to upload document: {str(e)}"
        )


@router.get(
    "/documents",
    response_model=DocumentListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all documents",
    description="Retrieve all documents for the current tenant",
    tags=["documents"],
)
async def list_documents(
    tenant_id: Annotated[str, Depends(get_current_tenant)] = None,
    repository: Annotated[PGVectorRepository, Depends(get_repository)] = None,
) -> DocumentListResponse:
    """List all documents for the current tenant.

    Args:
        tenant_id: Tenant identifier from header.
        repository: Database repository instance.

    Returns:
        DocumentListResponse: List of documents with total count.
    """
    try:
        documents = await repository.get_all_documents(tenant_id)

        return DocumentListResponse(
            documents=[DocumentDTO.model_validate(doc) for doc in documents], total=len(documents)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve documents: {str(e)}"
        )


@router.get(
    "/documents/{document_id}",
    response_model=DocumentDTO,
    status_code=status.HTTP_200_OK,
    summary="Get document by ID",
    description="Retrieve a specific document by its ID",
    tags=["documents"],
)
async def get_document(
    document_id: str = Path(..., description="Document unique identifier"),
    tenant_id: Annotated[str, Depends(get_current_tenant)] = None,
    repository: Annotated[PGVectorRepository, Depends(get_repository)] = None,
) -> DocumentDTO:
    """Get a specific document by ID.

    Args:
        document_id: Document unique identifier.
        tenant_id: Tenant identifier from header.
        repository: Database repository instance.

    Returns:
        DocumentDTO: Document information.

    Raises:
        HTTPException: If document is not found.
    """
    try:
        document = await repository.get_document(tenant_id, document_id)

        if not document:
            raise DocumentNotFoundError(tenant_id, document_id)

        return DocumentDTO.model_validate(document)

    except DocumentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve document: {str(e)}"
        )


@router.delete(
    "/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete document",
    description="Delete a document and all its associated chunks",
    tags=["documents"],
    response_model=None,
)
async def delete_document(
    document_id: str = Path(..., description="Document unique identifier"),
    tenant_id: Annotated[str, Depends(get_current_tenant)] = None,
    repository: Annotated[PGVectorRepository, Depends(get_repository)] = None,
):
    """Delete a document and all its associated chunks.

    Args:
        document_id: Document unique identifier.
        tenant_id: Tenant identifier from header.
        repository: Database repository instance.

    Raises:
        HTTPException: If document is not found or deletion fails.
    """
    try:
        # Check if document exists
        document = await repository.get_document(tenant_id, document_id)
        if not document:
            raise DocumentNotFoundError(tenant_id, document_id)

        # Delete chunks first (cascade should handle this, but being explicit)
        await repository.delete_chunks(tenant_id, document_id)

        # Delete document
        deleted = await repository.delete_document(tenant_id, document_id)

        if not deleted:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete document")

    except DocumentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete document: {str(e)}"
        )


@router.get(
    "/documents/{document_id}/status",
    response_model=DocumentStatusDTO,
    status_code=status.HTTP_200_OK,
    summary="Get document processing status",
    description="Get the processing status of a document including chunk count",
    tags=["documents"],
)
async def get_document_status(
    document_id: str = Path(..., description="Document unique identifier"),
    tenant_id: Annotated[str, Depends(get_current_tenant)] = None,
    repository: Annotated[PGVectorRepository, Depends(get_repository)] = None,
) -> DocumentStatusDTO:
    """Get document processing status.

    Args:
        document_id: Document unique identifier.
        tenant_id: Tenant identifier from header.
        repository: Database repository instance.

    Returns:
        DocumentStatusDTO: Document status information.

    Raises:
        HTTPException: If document is not found.
    """
    try:
        document = await repository.get_document(tenant_id, document_id)

        if not document:
            raise DocumentNotFoundError(tenant_id, document_id)

        # Get chunk count
        chunks = await repository.get_chunks(tenant_id, document_id)

        return DocumentStatusDTO(
            id=document.id,
            status=document.status,
            chunk_count=len(chunks),
            error_message=None if document.status == DocumentStatusEnum.processed else "Processing failed",
        )

    except DocumentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve document status: {str(e)}"
        )


@router.get(
    "/documents/{document_id}/chunks",
    response_model=ChunkListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get document chunks",
    description="Retrieve all chunks for a specific document",
    tags=["documents"],
)
async def get_document_chunks(
    document_id: str = Path(..., description="Document unique identifier"),
    tenant_id: Annotated[str, Depends(get_current_tenant)] = None,
    repository: Annotated[PGVectorRepository, Depends(get_repository)] = None,
) -> ChunkListResponse:
    """Get all chunks for a specific document.

    Args:
        document_id: Document unique identifier.
        tenant_id: Tenant identifier from header.
        repository: Database repository instance.

    Returns:
        ChunkListResponse: List of chunks with total count.

    Raises:
        HTTPException: If document is not found.
    """
    try:
        # Check if document exists
        document = await repository.get_document(tenant_id, document_id)
        if not document:
            raise DocumentNotFoundError(tenant_id, document_id)

        # Get chunks
        chunks = await repository.get_chunks(tenant_id, document_id)

        return ChunkListResponse(
            document_id=uuid.UUID(document_id),
            chunks=[ChunkDTO.model_validate(chunk) for chunk in chunks],
            total=len(chunks),
        )

    except DocumentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve chunks: {str(e)}"
        )
