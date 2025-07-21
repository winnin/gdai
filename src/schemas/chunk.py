# from uuid import UUID

# from pydantic import BaseModel, Field, ValidationInfo, field_validator


# class DocumentChunk(BaseModel):
#     """Represents a chunk of text extracted from a document.

#     Attributes:
#         id (str): Unique identifier for the text chunk.
#         tenant_id (str): Identifier for the tenant.
#         document_id (str): Unique identifier for the document.
#         type (str): Type of the chunk (e.g., "paragraph", "heading", etc.).
#         chunk (str): The text content of the chunk.
#         page_number (int): Page number from which the chunk was extracted.
#         embedding (list[float] | None): Embedding vector for the text chunk, if available.
#         created_at (str | None): Timestamp when the chunk was created.
#         updated_at (str | None): Timestamp when the chunk was last updated.
#     """

#     id: str | UUID | None = Field(default=None)
#     tenant_id: str
#     document_id: str
#     type: str
#     chunk: str = Field(min_length=1)
#     page_number: int = Field(ge=0)  # Must be >= 0
#     embedding: list[float] | None = Field(default_factory=list)
#     created_at: str | None = Field(default=None)
#     updated_at: str | None = Field(default=None)

#     model_config = {
#         "from_attributes": True  # Allow conversion from SQLAlchemy models to Pydantic models
#     }

#     def __str__(self) -> str:
#         """Return a human-readable string representation of the DocumentChunk.

#         Returns:
#             str: A string displaying the chunk ID, page number, and offsets.
#         """
#         return f"DocumentChunk(chunk_id={self.id}, page_number={self.page_number}, offsets=({self.begin_offset}, {self.end_offset}))"

#     @field_validator("page_number")
#     def validate_page_number(cls, value, _: ValidationInfo):
#         if value < 0:
#             raise ValueError("page_number deve ser maior ou igual a 0")
#         return value

#     @field_validator("embedding")
#     def validate_embedding(cls, value, _: ValidationInfo):
#         if value is not None and not all(isinstance(x, float) for x in value):
#             raise ValueError("Todos os elementos de embedding devem ser float")
#         return value

#     @field_validator("chunk")
#     def validate_chunk(cls, value, _: ValidationInfo):
#         if not value or not value.strip():
#             raise ValueError("chunk não pode ser vazio")
#         return value

#     @field_validator("id", "tenant_id", "document_id", "type")
#     def validate_non_empty_str(cls, value, info: ValidationInfo):
#         if not value or not isinstance(value, str) or not value.strip():
#             raise ValueError(f"{info.field_name} não pode ser vazio")
#         return value
