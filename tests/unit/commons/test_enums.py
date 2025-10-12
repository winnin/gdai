"""Unit tests for gdai.commons.enums module."""

from gdai.commons.enums import ChunkTypeEnum, DocumentStatusEnum, DocumentTypeEnum, QueryStatusEnum


class TestEnums:
    """Test suite for gdai.commons.enums module."""

    def test_document_status_enum_values(self):
        """Test DocumentStatusEnum has expected values."""
        assert DocumentStatusEnum.processed.value == "processed"
        assert DocumentStatusEnum.extraction_failed.value == "extraction_failed"
        assert DocumentStatusEnum.embedding_failed.value == "embedding_failed"

    def test_document_status_enum_is_string(self):
        """Test DocumentStatusEnum inherits from str."""
        assert isinstance(DocumentStatusEnum.processed, str)
        assert isinstance(DocumentStatusEnum.extraction_failed, str)

    def test_document_type_enum_values(self):
        """Test DocumentTypeEnum has expected values."""
        assert DocumentTypeEnum.pdf.value == "pdf"

    def test_document_type_enum_is_string(self):
        """Test DocumentTypeEnum inherits from str."""
        assert isinstance(DocumentTypeEnum.pdf, str)

    def test_chunk_type_enum_values(self):
        """Test ChunkTypeEnum has expected values."""
        assert ChunkTypeEnum.text.value == "text"
        assert ChunkTypeEnum.image.value == "image"
        assert ChunkTypeEnum.table.value == "table"

    def test_chunk_type_enum_is_string(self):
        """Test ChunkTypeEnum inherits from str."""
        assert isinstance(ChunkTypeEnum.text, str)
        assert isinstance(ChunkTypeEnum.image, str)
        assert isinstance(ChunkTypeEnum.table, str)

    def test_query_status_enum_values(self):
        """Test QueryStatusEnum has expected values."""
        assert QueryStatusEnum.pending.value == "pending"
        assert QueryStatusEnum.completed.value == "completed"
        assert QueryStatusEnum.failed.value == "failed"

    def test_query_status_enum_is_string(self):
        """Test QueryStatusEnum inherits from str."""
        assert isinstance(QueryStatusEnum.pending, str)
        assert isinstance(QueryStatusEnum.completed, str)

    def test_enum_equality(self):
        """Test enum values can be compared."""
        status1 = DocumentStatusEnum.processed
        status2 = DocumentStatusEnum.processed
        assert status1 == status2
        assert status1 == "processed"

    def test_enum_inequality(self):
        """Test different enum values are not equal."""
        status1 = DocumentStatusEnum.processed
        status2 = DocumentStatusEnum.extraction_failed
        assert status1 != status2

    def test_enum_in_collection(self):
        """Test enum values work in collections."""
        statuses = {DocumentStatusEnum.processed, DocumentStatusEnum.extraction_failed}
        assert DocumentStatusEnum.processed in statuses
        assert DocumentStatusEnum.embedding_failed not in statuses
