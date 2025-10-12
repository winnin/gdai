"""Unit tests for document extraction activities."""

import json

import pytest

from gdai.temporal.extract_document.activity import (
    extract_document_content,
    save_document_metadata,
    validate,
)
from gdai.temporal.extract_document.schema import DocumentExtracInput


class TestValidateActivity:
    """Test suite for validate activity."""

    @pytest.mark.asyncio
    async def test_validate_valid_document(self, s3_storage, tmp_path, sample_tenant_id):
        """Test validation of valid S3 document."""
        # Upload document to S3
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"PDF content" * 100)  # Ensure > 0 bytes

        s3_key = s3_storage.upload_file(sample_tenant_id, str(test_file))

        # Validate
        input_data = DocumentExtracInput(s3_key=s3_key, tenant_id=sample_tenant_id, chunk_strategy="semantic")

        # Should not raise exception
        await validate(input_data)

    @pytest.mark.asyncio
    async def test_validate_nonexistent_document(self, sample_tenant_id):
        """Test validation fails for nonexistent document."""
        input_data = DocumentExtracInput(
            s3_key="nonexistent/file.pdf",
            tenant_id=sample_tenant_id,
            chunk_strategy="semantic",
        )

        with pytest.raises(FileNotFoundError):
            await validate(input_data)

    @pytest.mark.asyncio
    async def test_validate_empty_document(self, s3_storage, tmp_path, sample_tenant_id):
        """Test validation fails for empty document."""
        # Upload empty file
        test_file = tmp_path / "empty.pdf"
        test_file.write_bytes(b"")

        s3_key = s3_storage.upload_file(sample_tenant_id, str(test_file))

        input_data = DocumentExtracInput(s3_key=s3_key, tenant_id=sample_tenant_id, chunk_strategy="semantic")

        with pytest.raises(ValueError, match="empty"):
            await validate(input_data)

    @pytest.mark.asyncio
    async def test_validate_file_too_large(self, s3_storage, tmp_path, sample_tenant_id, monkeypatch):
        """Test validation fails for files exceeding size limit."""
        # Mock get_settings to return settings with very small file size limit
        from unittest.mock import MagicMock

        # Create a mock that returns small max_file_size_mb
        mock_settings = MagicMock()
        mock_settings.extractor = MagicMock()
        mock_settings.extractor.max_file_size_mb = 0.001  # 1KB limit (0.001 MB)

        # Monkeypatch get_settings to return our mock
        monkeypatch.setattr("gdai.temporal.extract_document.activity.get_settings", lambda: mock_settings)

        # Upload 2KB file
        test_file = tmp_path / "large.pdf"
        test_file.write_bytes(b"x" * 2048)  # 2KB

        s3_key = s3_storage.upload_file(sample_tenant_id, str(test_file))

        input_data = DocumentExtracInput(s3_key=s3_key, tenant_id=sample_tenant_id, chunk_strategy="semantic")

        with pytest.raises(ValueError, match="exceeds maximum"):
            await validate(input_data)

    @pytest.mark.asyncio
    async def test_validate_invalid_tenant_id(self, s3_storage, tmp_path):
        """Test validation with invalid tenant_id."""
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"content")
        s3_key = s3_storage.upload_file("valid-tenant", str(test_file))

        input_data = DocumentExtracInput(s3_key=s3_key, tenant_id="", chunk_strategy="semantic")

        with pytest.raises(ValueError):
            await validate(input_data)

    @pytest.mark.asyncio
    async def test_validate_invalid_s3_key(self, sample_tenant_id):
        """Test validation with invalid s3_key."""
        input_data = DocumentExtracInput(s3_key="", tenant_id=sample_tenant_id, chunk_strategy="semantic")

        with pytest.raises(ValueError):
            await validate(input_data)


class TestSaveDocumentMetadataActivity:
    """Test suite for save_document_metadata activity."""

    @pytest.mark.asyncio
    async def test_save_document_metadata(self, db_session, sample_tenant_id):
        """Test saving document metadata to database."""
        s3_key = f"{sample_tenant_id}/document.pdf"

        input_data = DocumentExtracInput(s3_key=s3_key, tenant_id=sample_tenant_id, chunk_strategy="semantic")

        doc_id = await save_document_metadata(input_data)

        # Verify
        assert doc_id is not None
        assert isinstance(doc_id, str)

        # Verify in database
        from gdai.repositories import RepositoryFactory

        async with RepositoryFactory.get_repository() as repo:
            doc = await repo.get_document(sample_tenant_id, doc_id)

        assert doc is not None
        assert doc.name == "document.pdf"
        assert doc.s3_path == s3_key
        assert doc.tenant_id == sample_tenant_id

    @pytest.mark.asyncio
    async def test_save_document_metadata_extracts_filename(self, db_session, sample_tenant_id):
        """Test that filename is correctly extracted from S3 key."""
        s3_key = f"{sample_tenant_id}/subfolder/my-document.pdf"

        input_data = DocumentExtracInput(s3_key=s3_key, tenant_id=sample_tenant_id, chunk_strategy="semantic")

        doc_id = await save_document_metadata(input_data)

        # Verify filename extraction
        from gdai.repositories import RepositoryFactory

        async with RepositoryFactory.get_repository() as repo:
            doc = await repo.get_document(sample_tenant_id, doc_id)

        assert doc.name == "my-document.pdf"

    @pytest.mark.asyncio
    async def test_save_document_metadata_different_types(self, db_session, sample_tenant_id):
        """Test saving documents with different file types."""
        # Only test PDF since it's the only supported type currently
        file_types = ["pdf"]

        for file_type in file_types:
            s3_key = f"{sample_tenant_id}/document.{file_type}"

            input_data = DocumentExtracInput(s3_key=s3_key, tenant_id=sample_tenant_id, chunk_strategy="semantic")

            doc_id = await save_document_metadata(input_data)

            # Verify type is correctly set
            from gdai.repositories import RepositoryFactory

            async with RepositoryFactory.get_repository() as repo:
                doc = await repo.get_document(sample_tenant_id, doc_id)

            assert doc.type.value == file_type


class TestExtractDocumentContentActivity:
    """Test suite for extract_document_content activity."""

    @pytest.mark.asyncio
    async def test_extract_document_content_pdf(self, s3_storage, sample_pdf_path, sample_tenant_id):
        """Test extracting content from PDF document."""
        # Upload PDF to S3
        s3_key = s3_storage.upload_file(sample_tenant_id, str(sample_pdf_path))

        input_data = DocumentExtracInput(s3_key=s3_key, tenant_id=sample_tenant_id, chunk_strategy="semantic")

        # Extract
        extracted_path = await extract_document_content(input_data)

        # Verify output file exists and contains JSON
        assert extracted_path.endswith(".json")
        with open(extracted_path) as f:
            data = json.load(f)
            assert "texts" in data
            assert len(data["texts"]) > 0

    @pytest.mark.asyncio
    async def test_extract_cleans_up_downloaded_file(self, s3_storage, sample_pdf_path, sample_tenant_id):
        """Test that temporary downloaded file is cleaned up after extraction."""
        import os

        # Upload PDF
        s3_key = s3_storage.upload_file(sample_tenant_id, str(sample_pdf_path))

        input_data = DocumentExtracInput(s3_key=s3_key, tenant_id=sample_tenant_id, chunk_strategy="semantic")

        # Get temp folder
        from gdai.commons.settings import get_settings

        tmp_folder = get_settings().extractor.tmp_folder

        # Count files before
        files_before = set(os.listdir(tmp_folder))

        # Extract
        await extract_document_content(input_data)

        # Count files after (should not have extra downloaded file)
        files_after = set(os.listdir(tmp_folder))

        # Only the output JSON should remain, not the downloaded PDF
        new_files = files_after - files_before
        assert all(f.endswith(".json") for f in new_files)

    @pytest.mark.asyncio
    async def test_extract_handles_s3_download_error(self, sample_tenant_id):
        """Test error handling when S3 download fails."""
        input_data = DocumentExtracInput(
            s3_key="nonexistent/file.pdf",
            tenant_id=sample_tenant_id,
            chunk_strategy="semantic",
        )

        with pytest.raises(Exception):  # Should propagate S3 error
            await extract_document_content(input_data)

    @pytest.mark.asyncio
    async def test_extract_different_document_types(self, s3_storage, sample_pdf_path, sample_tenant_id):
        """Test extraction with different document types."""
        # Test with PDF
        s3_key = s3_storage.upload_file(sample_tenant_id, str(sample_pdf_path), "test.pdf")

        input_data = DocumentExtracInput(s3_key=s3_key, tenant_id=sample_tenant_id, chunk_strategy="semantic")

        extracted_path = await extract_document_content(input_data)

        assert extracted_path is not None
        assert extracted_path.endswith(".json")

    @pytest.mark.asyncio
    async def test_extract_output_format(self, s3_storage, sample_pdf_path, sample_tenant_id):
        """Test that extracted output has the expected format."""
        s3_key = s3_storage.upload_file(sample_tenant_id, str(sample_pdf_path))

        input_data = DocumentExtracInput(s3_key=s3_key, tenant_id=sample_tenant_id, chunk_strategy="semantic")

        extracted_path = await extract_document_content(input_data)

        # Verify output format
        with open(extracted_path) as f:
            data = json.load(f)

            # Should have required fields
            assert "texts" in data
            assert isinstance(data["texts"], list)

            # Each text entry should have page number and content
            if len(data["texts"]) > 0:
                first_entry = data["texts"][0]
                assert isinstance(first_entry, list)
                assert len(first_entry) == 2  # [page_number, content]


class TestExtractActivitiesIntegration:
    """Integration tests for multiple extraction activities working together."""

    @pytest.mark.asyncio
    async def test_full_extraction_flow(self, s3_storage, sample_pdf_path, db_session, sample_tenant_id):
        """Test complete extraction flow: validate -> save metadata -> extract."""
        # Upload document
        s3_key = s3_storage.upload_file(sample_tenant_id, str(sample_pdf_path))

        input_data = DocumentExtracInput(s3_key=s3_key, tenant_id=sample_tenant_id, chunk_strategy="semantic")

        # Step 1: Validate
        await validate(input_data)

        # Step 2: Save metadata
        doc_id = await save_document_metadata(input_data)
        assert doc_id is not None

        # Step 3: Extract content
        extracted_path = await extract_document_content(input_data)
        assert extracted_path is not None

        # Verify document in database
        from gdai.repositories import RepositoryFactory

        async with RepositoryFactory.get_repository() as repo:
            doc = await repo.get_document(sample_tenant_id, doc_id)

        assert doc is not None
        assert doc.s3_path == s3_key
