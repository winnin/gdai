from __future__ import annotations

from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    """
    Response model for document upload endpoint.
    """

    message: str
    document_name: str
    tenant_id: str
    status: str
