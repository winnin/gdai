from uuid import UUID

from pydantic import BaseModel, Field, ValidationInfo, field_validator


def __uuid_to_str(v: UUID | str | None) -> str | None:
    """Convert UUID objects to strings.

    Args:
        v: A UUID object, string, or None

    Returns:
        The string representation of the UUID or None
    """
    if v is None:
        return None
    if isinstance(v, UUID):
        return str(v)
    return v


class Text(BaseModel):
    """Represents a text content extracted from a document page.

    Attributes:
        page (int): The page number from which the text was extracted.
        text (str): The extracted text content.
    """

    page: int
    text: str

    def __str__(self) -> str:
        """Return a human-readable string representation of the Page.

        Returns:
            str: A string displaying the page number and a snippet of the text.
        """
        return f"Page {self.page}: {self.text[:500]}..."

    def __len__(self) -> int:
        """Return the length of the text content.

        Returns:
            int: The length of the text content.
        """
        return len(self.text)

    def __getitem__(self, key):
        """Permite fatiar o conteúdo do texto como uma string normal.

        Args:
            key (int ou slice): Índice ou fatia a ser acessada.

        Returns:
            str: Parte do texto correspondente.
        """
        return self.text[key]


class Image(BaseModel):
    """Represents an image extracted from a document page.

    Attributes:
        page (int): The page number where the image is located.
        position_x (int): The x-coordinate of the image's position.
        position_y (int): The y-coordinate of the image's position.
        width (int): The width of the image in pixels.
        height (int): The height of the image in pixels.
    """

    page: int
    position_x: int
    position_y: int
    width: int
    height: int

    def __str__(self) -> str:
        """Return a human-readable string representation of the Image.

        Returns:
            str: A string displaying the page number and position information.
        """
        return f"Image on page {self.page}: Position({self.position_x}, {self.position_y}), Size({self.width}x{self.height})"


class Table(BaseModel):
    """Represents a table extracted from a document page.

    Attributes:
        page (int): The page number where the table is located.
        cells (list[dict]): A list of dictionaries, each representing a cell in the table
                          with its content and position information.
    """

    page: int
    cells: list[dict]

    def __str__(self) -> str:
        """Return a human-readable string representation of the Table.

        Returns:
            str: A string displaying the page number and number of cells.
        """
        return f"Table on page {self.page}: {len(self.cells)} cells"


class Document(BaseModel):
    """Represents a document with its content and metadata.

    A document can contain text content, tables, and images extracted from
    the original document file.

    Attributes:
        id (str | None): Unique identifier for the document. Defaults to empty string.
        tenant_id (str | None): Identifier for the tenant. Defaults to empty string.
        name (str): The name or title of the document.
        status (str): Current status of the document (e.g., "processing", "completed").
        type (str): The type or format of the document (e.g., "pdf", "docx").
        texts (list[Text]): List of text elements extracted from the document.
        tables (list[Table] | None): List of tables extracted from the document, if any.
        images (list[Image] | None): List of images extracted from the document, if any.
        created_at (str | None): Timestamp when the document was created. Defaults to None.
        updated_at (str | None): Timestamp when the document was last updated. Defaults to None.
    """

    id: str | UUID | None = Field(default="")
    tenant_id: str | None = Field(default="")
    name: str
    status: str
    type: str
    texts: list[Text] | None = Field(default_factory=list)
    tables: list[Table] | None = Field(default_factory=list)
    images: list[Image] | None = Field(default_factory=list)
    created_at: str | None = Field(default=None)
    updated_at: str | None = Field(default=None)

    model_config = {
        "from_attributes": True  # Allow conversion from SQLAlchemy models to Pydantic models
    }

    def __str__(self) -> str:
        """Return a human-readable string representation of the Document.

        Returns:
            str: A string displaying the document ID, name, and number of pages.
        """
        return f"Name: {self.name}, Pages: {len(self.texts) }, Type: {self.type}, Status: {self.status}"

    @field_validator("id")
    def validate_id(cls, v):
        return __uuid_to_str(v)


class DocumentChunk(BaseModel):
    """Represents a chunk of text extracted from a document.

    Attributes:
        id (str): Unique identifier for the text chunk.
        tenant_id (str): Identifier for the tenant.
        document_id (str): Unique identifier for the document.
        type (str): Type of the chunk (e.g., "paragraph", "heading", etc.).
        chunk (str): The text content of the chunk.
        page_number (int): Page number from which the chunk was extracted.
        embedding (list[float] | None): Embedding vector for the text chunk, if available.
        created_at (str | None): Timestamp when the chunk was created.
        updated_at (str | None): Timestamp when the chunk was last updated.
    """

    id: str | UUID | None = Field(default=None)
    tenant_id: str
    document_id: str
    type: str
    chunk: str = Field(min_length=1)
    page_number: int = Field(ge=0)  # Must be >= 0
    embedding: list[float] | None = Field(default_factory=list)
    created_at: str | None = Field(default=None)
    updated_at: str | None = Field(default=None)

    model_config = {
        "from_attributes": True  # Allow conversion from SQLAlchemy models to Pydantic models
    }

    def __str__(self) -> str:
        """Return a human-readable string representation of the DocumentChunk.

        Returns:
            str: A string displaying the chunk ID, page number, and offsets.
        """
        return f"DocumentChunk(chunk_id={self.id}, page_number={self.page_number}, offsets=({self.begin_offset}, {self.end_offset}))"

    @field_validator("page_number")
    def validate_page_number(cls, value, _: ValidationInfo):
        if value < 0:
            raise ValueError("page_number deve ser maior ou igual a 0")
        return value

    @field_validator("embedding")
    def validate_embedding(cls, value, _: ValidationInfo):
        if value is not None and not all(isinstance(x, float) for x in value):
            raise ValueError("Todos os elementos de embedding devem ser float")
        return value

    @field_validator("chunk")
    def validate_chunk(cls, value, _: ValidationInfo):
        if not value or not value.strip():
            raise ValueError("chunk não pode ser vazio")
        return value

    @field_validator("id", "tenant_id", "document_id", "type")
    def validate_non_empty_str(cls, value, info: ValidationInfo):
        if not value or not isinstance(value, str) or not value.strip():
            raise ValueError(f"{info.field_name} não pode ser vazio")
        return value

    @field_validator("id")
    def validate_id(cls, v):
        return __uuid_to_str(v)


class QueryDocumentChunk(DocumentChunk):
    """
    Represents a document chunk with additional fields for user queries.
    Attributes:
        similarity: Similarity score between the query and the chunk.
        similarity_type: Type of similarity metric used (e.g., cosine, dot_product).
    """

    similarity: float = Field(default=0.0)
    similarity_type: str = Field(default="cosine", description="Type of similarity metric used (e.g., cosine, dot_product).")
    model_config = {
        "from_attributes": True  # Allow conversion from SQLAlchemy models to Pydantic models
    }


class Query(BaseModel):
    """Represents a  query for searching document chunks.
    Attributes:
        id: Unique identifier for the query (optional).
        tenant_id: Identifier for the tenant context of the query.
        query: The search query text (1-1000 characters).
        result: The result of the query (optional).
        status: Status of the query (default: "pending").
        num_chunks: Number of relevant chunks to retrieve (1-1000).
        created_at: Timestamp when the query was created (optional).
        updated_at: Timestamp when the query was last updated (optional).
        chunks: List of document chunks related to this query.
    """

    id: str | UUID | None = Field(default=None)
    tenant_id: str
    query: str = Field(min_length=1, max_length=1000)
    result: str | None = Field(default=None)
    status: str = Field(default="pending")
    created_at: str | None = Field(default=None)
    updated_at: str | None = Field(default=None)
    chunks: list[QueryDocumentChunk] = Field(default_factory=list)

    model_config = {
        "from_attributes": True  # Allow conversion from SQLAlchemy models to Pydantic models
    }

    @field_validator("id")
    def validate_id(cls, v):
        return __uuid_to_str(v)
