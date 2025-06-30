from pydantic import BaseModel, Field, ValidationInfo, field_validator


class DocumentChunk(BaseModel):
    """Represents a chunk of text extracted from a document.

    Attributes:
        chunk_id (str): Unique identifier for the text chunk.
        tenant_id (str): Identifier for the tenant.
        doc_id (str): Unique identifier for the document.
        chunk_text (str): The text content of the chunk.
        page_number (int): Page number from which the chunk was extracted.
        begin_offset (int): Starting offset within the page.
        end_offset (int): Ending offset within the page.
        embedding (Optional[list[float]]): Embedding vector for the text chunk, if available.
        doc_id (str): The ID of the document the chunk belongs to.
    """

    tenant_id: str
    chunk_id: str
    doc_id: str
    doc_name: str
    chunk_text: str = Field(min_length=1)
    page_number: int = Field(ge=0)  # Must be >= 0
    begin_offset: int = Field(ge=0)  # Must be >= 0
    end_offset: int = Field(ge=0)  # Must be >= 0
    embedding: list[float] | None = Field(default_factory=list)

    def __str__(self) -> str:
        """Return a human-readable string representation of the DocumentChunk.

        Returns:
            str: A string displaying the chunk ID, page number, and offsets.
        """
        return f"DocumentChunk(chunk_id={self.chunk_id}, page_number={self.page_number}, offsets=({self.begin_offset}, {self.end_offset}))"

    @field_validator("end_offset")
    def validate_end_offset(cls, value, info: ValidationInfo):
        """Validates that the end offset is greater than or equal to the begin offset.

        Args:
            value (int): The end offset to validate.
            info (ValidationInfo): Additional validation context.

        Returns:
            int: The validated end offset.

        Raises:
            ValueError: If the end offset is less than the begin offset.
        """
        begin_offset = info.data["begin_offset"]
        if begin_offset is None:
            raise ValueError("begin_offset must be provided before validating end_offset")
        if value < begin_offset:
            raise ValueError("end_offset must be greater than or equal to begin_offset")
        return value
