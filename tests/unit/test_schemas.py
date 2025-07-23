import pytest
from pydantic import ValidationError

from src.schemas import Document, DocumentChunk, Image, Table, Text


class TestTextSchema:
    """Test suite for the Text schema."""

    def test_valid_text_creation(self):
        """Test creating a valid Text instance."""
        text = Text(page=1, text="Sample text content")
        assert text.page == 1
        assert text.text == "Sample text content"

    def test_text_str_method(self):
        """Test the string representation of Text."""
        text = Text(page=1, text="Sample text content")
        assert str(text).startswith("Page 1: Sample text content")

    def test_text_len_method(self):
        """Test the length method of Text."""
        text = Text(page=1, text="Sample text content")
        assert len(text) == len("Sample text content")

    def test_text_getitem_method(self):
        """Test the getitem method of Text."""
        text = Text(page=1, text="Sample text content")
        assert text[0:6] == "Sample"

    def test_text_missing_required_field(self):
        """Test validation error when required field is missing."""
        with pytest.raises(ValidationError):
            Text(page=1)  # Missing 'text' field

        with pytest.raises(ValidationError):
            Text(text="Sample")  # Missing 'page' field


class TestImageSchema:
    """Test suite for the Image schema."""

    def test_valid_image_creation(self):
        """Test creating a valid Image instance."""
        image = Image(page=1, position_x=10, position_y=20, width=200, height=150)
        assert image.page == 1
        assert image.position_x == 10
        assert image.position_y == 20
        assert image.width == 200
        assert image.height == 150

    def test_image_str_method(self):
        """Test the string representation of Image."""
        image = Image(page=1, position_x=10, position_y=20, width=200, height=150)
        expected_str = "Image on page 1: Position(10, 20), Size(200x150)"
        assert str(image) == expected_str

    def test_image_missing_required_field(self):
        """Test validation error when required fields are missing."""
        with pytest.raises(ValidationError):
            Image(position_x=10, position_y=20, width=200, height=150)  # Missing 'page'

        with pytest.raises(ValidationError):
            Image(page=1, position_y=20, width=200, height=150)  # Missing 'position_x'

        with pytest.raises(ValidationError):
            Image(page=1, position_x=10, width=200, height=150)  # Missing 'position_y'

        with pytest.raises(ValidationError):
            Image(page=1, position_x=10, position_y=20, height=150)  # Missing 'width'

        with pytest.raises(ValidationError):
            Image(page=1, position_x=10, position_y=20, width=200)  # Missing 'height'


class TestTableSchema:
    """Test suite for the Table schema."""

    def test_valid_table_creation(self):
        """Test creating a valid Table instance."""
        cells = [
            {"content": "Cell 1", "position_x": 0, "position_y": 0, "width": 100, "height": 50},
            {"content": "Cell 2", "position_x": 100, "position_y": 0, "width": 100, "height": 50},
        ]
        table = Table(page=1, cells=cells)
        assert table.page == 1
        assert len(table.cells) == 2
        assert table.cells[0]["content"] == "Cell 1"
        assert table.cells[1]["content"] == "Cell 2"

    def test_table_str_method(self):
        """Test the string representation of Table."""
        cells = [
            {"content": "Cell 1", "position_x": 0, "position_y": 0, "width": 100, "height": 50},
            {"content": "Cell 2", "position_x": 100, "position_y": 0, "width": 100, "height": 50},
        ]
        table = Table(page=1, cells=cells)
        assert str(table) == "Table on page 1: 2 cells"

    def test_empty_table(self):
        """Test creating a Table with no cells."""
        table = Table(page=1, cells=[])
        assert table.page == 1
        assert len(table.cells) == 0
        assert str(table) == "Table on page 1: 0 cells"

    def test_table_missing_required_field(self):
        """Test validation error when required fields are missing."""
        cells = [{"content": "Cell 1", "position_x": 0, "position_y": 0, "width": 100, "height": 50}]

        with pytest.raises(ValidationError):
            Table(cells=cells)  # Missing 'page'

        with pytest.raises(ValidationError):
            Table(page=1)  # Missing 'cells'


class TestDocumentSchema:
    """Test suite for the Document schema."""

    def test_valid_document_creation(self):
        """Test creating a valid Document instance with minimal fields."""
        doc = Document(name="test_document.pdf", status="processed", type="pdf", texts=[Text(page=1, text="Sample content")])
        assert doc.name == "test_document.pdf"
        assert doc.status == "processed"
        assert doc.type == "pdf"
        assert len(doc.texts) == 1
        assert doc.id == ""  # Default value
        assert doc.tenant_id == ""  # Default value
        assert isinstance(doc.tables, list)
        assert len(doc.tables) == 0  # Default empty list
        assert isinstance(doc.images, list)
        assert len(doc.images) == 0  # Default empty list

    def test_document_with_all_fields(self):
        """Test creating a Document instance with all fields."""
        doc = Document(
            id="doc-123",
            tenant_id="tenant-456",
            name="complete_document.pdf",
            status="processed",
            type="pdf",
            texts=[Text(page=1, text="Text content")],
            tables=[Table(page=1, cells=[{"content": "Cell 1", "position_x": 0, "position_y": 0, "width": 100, "height": 50}])],
            images=[Image(page=2, position_x=10, position_y=20, width=200, height=100)],
        )
        assert doc.id == "doc-123"
        assert doc.tenant_id == "tenant-456"
        assert len(doc.texts) == 1
        assert len(doc.tables) == 1
        assert len(doc.images) == 1

    def test_document_str_method(self):
        """Test the string representation of Document."""
        doc = Document(id="doc-123", tenant_id="tenant-456", name="test_document.pdf", status="processed", type="pdf", texts=[Text(page=1, text="Sample content")])
        str_repr = str(doc)
        assert "test_document.pdf" in str_repr

    def test_document_missing_required_fields(self):
        """Test validation error when required fields are missing."""
        with pytest.raises(ValidationError):
            Document(status="processed", type="pdf", texts=[])  # Missing 'name'

        with pytest.raises(ValidationError):
            Document(name="test.pdf", type="pdf", texts=[])  # Missing 'status'

        with pytest.raises(ValidationError):
            Document(name="test.pdf", status="processed", texts=[])  # Missing 'type'


class TestDocumentChunk:
    """Test suite for the DocumentChunk schema."""

    @staticmethod
    def valid_chunk_data():
        return {
            "id": "chunk-1",
            "tenant_id": "tenant-1",
            "document_id": "doc-1",
            "type": "text",
            "chunk": "Conteúdo do chunk.",
            "page_number": 1,
            "embedding": [0.1, 0.2, 0.3],
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-02T00:00:00Z",
            "begin_offset": 0,
            "end_offset": 10,
        }

    def test_valid_document_chunk(self):
        data = self.valid_chunk_data()
        chunk = DocumentChunk(**data)
        assert chunk.id == data["id"]
        assert chunk.page_number == data["page_number"]

    @pytest.mark.parametrize(
        "field,value",
        [
            ("tenant_id", ""),
            ("document_id", ""),
            # ("type", ""),
        ],
    )
    def test_empty_string_fields_raise(self, field, value):
        data = self.valid_chunk_data()
        data[field] = value
        with pytest.raises(ValidationError):
            DocumentChunk(**data)

    def test_chunk_cannot_be_empty(self):
        data = self.valid_chunk_data()
        data["chunk"] = "   "
        with pytest.raises(ValidationError):
            DocumentChunk(**data)

    def test_page_number_negative(self):
        data = self.valid_chunk_data()
        data["page_number"] = -1
        with pytest.raises(ValidationError):
            DocumentChunk(**data)

    def test_embedding_must_be_float(self):
        data = self.valid_chunk_data()
        data["embedding"] = [0.1, "not-a-float", 0.3]
        with pytest.raises(ValidationError):
            DocumentChunk(**data)

    def test_embedding_can_be_none(self):
        data = self.valid_chunk_data()
        data["embedding"] = None
        chunk = DocumentChunk(**data)
        assert chunk.embedding is None

    def test_created_at_and_updated_at_can_be_none(self):
        data = self.valid_chunk_data()
        data["created_at"] = None
        data["updated_at"] = None
        chunk = DocumentChunk(**data)
        assert chunk.created_at is None
        assert chunk.updated_at is None
