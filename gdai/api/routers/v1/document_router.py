"""Document upload endpoints router."""

from __future__ import annotations

import os
import shutil

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)

from gdai.api.deps import get_document_service
from gdai.api.routers.v1.types import DocumentStatusResponse, DocumentUploadResponse
from gdai.background_tasks.extract_document_background_task import document_extractor
from gdai.config.logger import logger
from gdai.config.settings import ExtractorConfig

router = APIRouter(prefix="/document", tags=["document"])


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    tenant_id: str = Form(...),
    document: UploadFile = File(...),
):
    """Upload a document to be processed by the document extractor.
    Saves the file and triggers the extraction actor.
    """
    try:
        if not tenant_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="tenant_id is required")
        if not document:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document file is required",
            )
        document_folder_path = os.path.join(ExtractorConfig.FOLDER_RAW_DOC_PATH, tenant_id)
        if not document_folder_path:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Document storage path not configured",
            )
        os.makedirs(document_folder_path, exist_ok=True)
        file_path = os.path.join(document_folder_path, document.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(document.file, buffer)
        document_data = {"document_path": file_path, "tenant_id": tenant_id}
        document_extractor.send(document_data)
        logger.info(f"Document {document.filename} uploaded successfully for tenant: {tenant_id}")
        return DocumentUploadResponse(
            message=f"Document {document.filename} uploaded and queued for processing",
            document_name=document.filename,
            tenant_id=tenant_id,
            status="pending",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading document: {e!s}",
        )


@router.get("/{tenant_id}", response_model=list[DocumentStatusResponse])
async def get_documents(tenant_id: str, document_service=Depends(get_document_service)):
    """Get all documents for a specific tenant."""
    if not tenant_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="tenant_id is required")

    try:
        logger.info(f"Retrieving documents for tenant {tenant_id}")
        documents = await document_service.get_all_documents(tenant_id=tenant_id)

        documents_response = [
            DocumentStatusResponse(
                id=str(doc.id),
                name=doc.name,
                tenant_id=tenant_id,
                status=doc.status.value,
                chunk_strategy="sentence",  # Placeholder for actual chunk strategy
                created_at=doc.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
                updated_at=doc.updated_at.strftime("%Y-%m-%dT%H:%M:%S"),
            )
            for doc in documents
        ]
        logger.info(f"Retrieved {len(documents_response)} documents for tenant {tenant_id}")
        return documents_response
    except Exception as e:
        logger.error(f"Error retrieving documents: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving documents: {e!s}",
        )


@router.get("status/{tenant_id}/{document_id}", response_model=DocumentStatusResponse)
async def get_document_status(tenant_id: str, document_id: str, document_service=Depends(get_document_service)):
    """Get the status of a document upload."""
    try:
        logger.info(f"Retrieving status for document {document_id} in tenant {tenant_id}")
        doc = await document_service.get_document_by_id(tenant_id=tenant_id, document_id=document_id)

        response = DocumentStatusResponse(
            id=str(doc.id),
            name=doc.name,
            tenant_id=tenant_id,
            status=doc.status.value,
            chunk_strategy="sentence",  # Placeholder for actual chunk strategy
            created_at=doc.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
            updated_at=doc.updated_at.strftime("%Y-%m-%dT%H:%M:%S"),
        )
        return response
    except Exception as e:
        logger.error(f"Error retrieving document status: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving document status: {e!s}",
        )
