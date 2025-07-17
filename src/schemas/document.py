from pydantic import BaseModel, Field


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

    id: str | None = Field(default="")
    tenant_id: str | None = Field(default="")
    name: str
    status: str
    type: str
    texts: list[Text] | None = Field(default_factory=list)
    tables: list[Table] | None = Field(default_factory=list)
    images: list[Image] | None = Field(default_factory=list)
    created_at: str | None = Field(default=None)
    updated_at: str | None = Field(default=None)

    def __str__(self) -> str:
        """Return a human-readable string representation of the Document.

        Returns:
            str: A string displaying the document ID, name, and number of pages.
        """
        return f"Name: {self.name}, Pages: {len(self.texts) }, Type: {self.type}, Status: {self.status}"


class DocumentUploadResponse(BaseModel):
    """Response model for document upload endpoint."""

    message: str
    document_name: str
    tenant_id: str
    status: str
