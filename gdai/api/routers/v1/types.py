from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    message: str
    document_name: str
    tenant_id: str
    status: str = Field(default="pending")
