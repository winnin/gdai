from __future__ import annotations

from pydantic import BaseModel, Field, ValidationInfo, field_validator


class Text(BaseModel):
    """
    Represents a text content extracted from a document page.

    Attributes:
        page (int): The page number from which the text was extracted.
        text (str): The extracted text content.
    """

    page: int
    text: str

    def __str__(self) -> str:
        """
        Return a human-readable string representation of the Page.

        Returns:
            str: A string displaying the page number and a snippet of the text.
        """
        return f"Page {self.page}: {self.text[:500]}..."

    def __len__(self) -> int:
        """
        Return the length of the text content.

        Returns:
            int: The length of the text content.
        """
        return len(self.text)

    def __getitem__(self, key):
        """
        Permite fatiar o conteúdo do texto como uma string normal.

        Args:
            key (int ou slice): Índice ou fatia a ser acessada.

        Returns:
            str: Parte do texto correspondente.
        """
        return self.text[key]


class Image(BaseModel):
    """
    Represents an image extracted from a document page.

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
        """
        Return a human-readable string representation of the Image.

        Returns:
            str: A string displaying the page number and position information.
        """
        return f"Image on page {self.page}: Position({self.position_x}, {self.position_y}), Size({self.width}x{self.height})"


class Table(BaseModel):
    """
    Represents a table extracted from a document page.

    Attributes:
        page (int): The page number where the table is located.
        cells (list[dict]): A list of dictionaries, each representing a cell in the table
                          with its content and position information.
    """

    page: int
    cells: list[dict]

    def __str__(self) -> str:
        """
        Return a human-readable string representation of the Table.

        Returns:
            str: A string displaying the page number and number of cells.
        """
        return f"Table on page {self.page}: {len(self.cells)} cells"


class Document(BaseModel):
    """
    Represents a document with its content and metadata.

    A document can contain text content, tables, and images extracted from
    the original document file.

    Attributes:
        tenant_id (Optional[str]): Identifier for the tenant. Defaults to empty string.
        doc_id (str): Unique identifier for the document.
        doc_name (str): The name or title of the document.
        texts (list[Text]): List of text elements extracted from the document.
        tables (Optional[list[Table]]): List of tables extracted from the document, if any.
        images (Optional[list[Image]]): List of images extracted from the document, if any.
    """

    tenant_id: str | None = Field(default="")
    doc_id: str | None = Field(default="")
    doc_name: str
    texts: list[Text]
    tables: list[Table] | None = Field(default_factory=list)
    images: list[Image] | None = Field(default_factory=list)

    def __str__(self) -> str:
        """
        Return a human-readable string representation of the Document.

        Returns:
            str: A string displaying the document ID, name, and number of pages.
        """
        return f"Name: {self.doc_name}, Pages: {len(self.texts)}"


class DocumentChunk(BaseModel):
    """
    Represents a chunk of text extracted from a document.

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
        """
        Return a human-readable string representation of the DocumentChunk.

        Returns:
            str: A string displaying the chunk ID, page number, and offsets.
        """
        return f"DocumentChunk(chunk_id={self.chunk_id}, page_number={self.page_number}, offsets=({self.begin_offset}, {self.end_offset}))"

    @field_validator("end_offset")
    def validate_end_offset(cls, value, info: ValidationInfo):
        """
        Validates that the end offset is greater than or equal to the begin offset.

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
            raise ValueError(
                "begin_offset must be provided before validating end_offset"
            )
        if value < begin_offset:
            raise ValueError("end_offset must be greater than or equal to begin_offset")
        return value


class QueryInput(BaseModel):
    """Represents a user query with search parameters.

    Used to structure and validate search parameters submitted by users.

    Attributes:
        tenant_id: Identifier for the tenant context of the query.
        query: The search query text (1-1000 characters).
        num_chunks: Number of relevant chunks to retrieve (1-1000, default: 10).
        temperature: Controls randomness in response generation (0.0-1.0, default: 0.5).
    """

    tenant_id: str
    query: str = Field(min_length=1, max_length=1000)
    num_chunks: int = Field(ge=1, le=1000, default=10)

    def __str__(self) -> str:
        """Return a human-readable string representation of the QueryInput.

        Returns:
            A string displaying the query and parameters.
        """
        return f"QueryInput(query={self.query}, num_chunks={self.num_chunks})"


class ChunkQueryResult(BaseModel):
    """Represents a single chunk result from a search query.

    Stores individual search results with their relevance scores.

    Attributes:
        tenant_id: Identifier for the tenant context.
        query: The search query text that produced this result.
        chunk: The document chunk that matches the query.
        similarity: Similarity score between the query and the chunk.
    """

    tenant_id: str
    query_id: str
    chunk: DocumentChunk
    similarity: float

    def __str__(self) -> str:
        """Return a human-readable string representation of the ChunkQueryResult.

        Returns:
            A string displaying query, chunk ID, and similarity score.
        """
        return f"ChunkQueryResult(query={self.query_id}, chunk_id={self.chunk.chunk_id}, similarity={self.similarity})"


class QueryOutput(BaseModel):
    """Represents the complete response to a query.

    Encapsulates the complete response to a user query, including both
    the generated answer and the supporting evidence chunks.

    Attributes:
        tenant_id: Identifier for the tenant context.
        query: The original search query text.
        answer: Generated answer text based on the query and relevant chunks.
        chunk_result: List of chunks used to generate the answer.
        num_chunks: Number of chunks used in the response (0-1000, default: 0).
        temperature: Temperature value used for answer generation (0.0-1.0, default: 0.5).
    """

    tenant_id: str
    query: str
    answer: str
    chunk_result: list[ChunkQueryResult] = Field(default_factory=list)
    num_chunks: int = Field(ge=0, le=1000, default=0)
    temperature: float = Field(ge=0.0, le=1.0, default=0.5)

    def __str__(self) -> str:
        """Return a human-readable string representation of the QueryOutput.

        Returns:
            A string displaying query, answer, and chunk count.
        """
        return f"QueryOutput(query={self.query}, answer={self.answer}, num_chunks={self.num_chunks})"
