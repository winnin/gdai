import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    id: UUID | None = None
    tenant_id: str = Field(min_length=1)
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now())
    updated_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now())
