"""
Document upload endpoints router.
"""

from __future__ import annotations

import os
import shutil

from fastapi import (
    APIRouter,
    BackgroundTasks,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)

from src.actor.extractor.actor import document_extractor
from src.api.models.document import DocumentUploadResponse
from src.shared.conf import ExtractorConfig
from src.shared.logger import logger

router = APIRouter(prefix="/document", tags=["document"])


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    tenant_id: str = Form(...),
    document: UploadFile = File(...),
):
    """
    Upload a document to be processed by the document extractor.
    Saves the file and triggers the extraction actor.
    """
    try:
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="tenant_id is required"
            )
        if not document:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document file is required",
            )
        document_folder_path = ExtractorConfig.FOLDER_RAW_DOC_PATH
        if not document_folder_path:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Document storage path not configured",
            )
        os.makedirs(document_folder_path, exist_ok=True)
        file_path = os.path.join(document_folder_path, document.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(document.file, buffer)
        document_data = {"document_name": document.filename, "tenant_id": tenant_id}
        document_extractor.send(document_data)
        logger.info(
            f"Document {document.filename} uploaded successfully for tenant: {tenant_id}"
        )
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
