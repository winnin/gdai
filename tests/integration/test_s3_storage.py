"""Unit tests for S3StorageService."""

import pytest
from botocore.exceptions import ClientError

from gdai.services.s3_storage import S3StorageService, get_s3_storage


class TestS3StorageService:
    """Test suite for S3StorageService."""

    def test_get_s3_storage_singleton(self):
        """Test that get_s3_storage returns a service instance."""
        storage = get_s3_storage()
        assert isinstance(storage, S3StorageService)
        assert storage.bucket is not None

    def test_get_s3_key_format(self):
        """Test S3 key generation with tenant isolation."""
        storage = get_s3_storage()

        key = storage.get_s3_key("tenant-123", "document.pdf")

        assert key == "tenant-123/document.pdf"
        assert key.startswith("tenant-123/")

    def test_get_s3_key_with_special_characters(self):
        """Test S3 key generation with special characters in filename."""
        storage = get_s3_storage()

        key = storage.get_s3_key("tenant-123", "my document (1).pdf")

        assert key == "tenant-123/my document (1).pdf"
        assert key.startswith("tenant-123/")

    def test_upload_file(self, s3_storage, tmp_path, sample_tenant_id):
        """Test file upload to S3."""
        # Create test file
        test_file = tmp_path / "test.txt"
        test_content = "Test content for upload"
        test_file.write_text(test_content)

        # Upload
        s3_key = s3_storage.upload_file(tenant_id=sample_tenant_id, file_path=str(test_file))

        # Verify
        assert s3_key == f"{sample_tenant_id}/test.txt"
        assert s3_storage.file_exists(s3_key)

        # Verify content
        download_path = tmp_path / "downloaded.txt"
        s3_storage.download_file(s3_key, str(download_path))
        assert download_path.read_text() == test_content

    def test_upload_file_with_custom_name(self, s3_storage, tmp_path, sample_tenant_id):
        """Test file upload with custom object name."""
        test_file = tmp_path / "original.txt"
        test_file.write_text("Test content")

        # Upload with custom name
        s3_key = s3_storage.upload_file(
            tenant_id=sample_tenant_id,
            file_path=str(test_file),
            object_name="custom_name.txt",
        )

        assert s3_key == f"{sample_tenant_id}/custom_name.txt"
        assert s3_storage.file_exists(s3_key)

    def test_upload_fileobj(self, s3_storage, sample_tenant_id):
        """Test file object upload to S3."""
        from io import BytesIO

        # Create file-like object
        file_content = b"Test binary content"
        file_obj = BytesIO(file_content)

        # Upload
        s3_key = s3_storage.upload_fileobj(tenant_id=sample_tenant_id, file_obj=file_obj, object_name="test.bin")

        # Verify
        assert s3_key == f"{sample_tenant_id}/test.bin"
        assert s3_storage.file_exists(s3_key)

    def test_upload_nonexistent_file(self, s3_storage, sample_tenant_id):
        """Test upload fails for nonexistent file."""
        with pytest.raises(FileNotFoundError):
            s3_storage.upload_file(tenant_id=sample_tenant_id, file_path="/nonexistent/file.txt")

    def test_download_file(self, s3_storage, tmp_path, sample_tenant_id):
        """Test file download from S3."""
        # Upload first
        upload_file = tmp_path / "upload.txt"
        original_content = "Download test content"
        upload_file.write_text(original_content)

        s3_key = s3_storage.upload_file(sample_tenant_id, str(upload_file))

        # Download
        download_file = tmp_path / "download.txt"
        s3_storage.download_file(s3_key, str(download_file))

        # Verify content matches
        assert download_file.read_text() == original_content

    def test_download_creates_parent_directories(self, s3_storage, tmp_path, sample_tenant_id):
        """Test that download creates parent directories if they don't exist."""
        # Upload file
        upload_file = tmp_path / "test.txt"
        upload_file.write_text("Test")
        s3_key = s3_storage.upload_file(sample_tenant_id, str(upload_file))

        # Download to nested path that doesn't exist
        download_path = tmp_path / "nested" / "path" / "file.txt"
        s3_storage.download_file(s3_key, str(download_path))

        assert download_path.exists()
        assert download_path.read_text() == "Test"

    def test_download_nonexistent_file(self, s3_storage, tmp_path):
        """Test download fails for nonexistent file."""
        with pytest.raises(ClientError):
            s3_storage.download_file("nonexistent/file.txt", str(tmp_path / "download.txt"))

    def test_delete_file(self, s3_storage, tmp_path, sample_tenant_id):
        """Test file deletion from S3."""
        # Upload
        test_file = tmp_path / "delete_me.txt"
        test_file.write_text("Delete test")

        s3_key = s3_storage.upload_file(sample_tenant_id, str(test_file))
        assert s3_storage.file_exists(s3_key)

        # Delete
        s3_storage.delete_file(s3_key)

        # Verify deleted
        assert not s3_storage.file_exists(s3_key)

    def test_delete_nonexistent_file(self, s3_storage):
        """Test delete operation on nonexistent file (should not raise error)."""
        # S3 delete is idempotent - deleting nonexistent file should succeed
        try:
            s3_storage.delete_file("nonexistent/file.txt")
        except Exception as e:
            pytest.fail(f"Delete should not raise exception: {e}")

    def test_file_exists_true(self, s3_storage, tmp_path, sample_tenant_id):
        """Test file_exists returns True for existing file."""
        test_file = tmp_path / "exists.txt"
        test_file.write_text("Test")

        s3_key = s3_storage.upload_file(sample_tenant_id, str(test_file))

        assert s3_storage.file_exists(s3_key) is True

    def test_file_exists_false(self, s3_storage):
        """Test file_exists returns False for nonexistent file."""
        assert s3_storage.file_exists("nonexistent/file.txt") is False

    def test_list_files_single_tenant(self, s3_storage, tmp_path, sample_tenant_id):
        """Test listing files for a single tenant."""
        # Upload multiple files
        filenames = ["file1.txt", "file2.txt", "file3.pdf"]
        for filename in filenames:
            file_path = tmp_path / filename
            file_path.write_text(f"Content of {filename}")
            s3_storage.upload_file(sample_tenant_id, str(file_path))

        # List files
        files = s3_storage.list_files(sample_tenant_id)

        # Verify
        assert len(files) == 3
        assert all(f.startswith(f"{sample_tenant_id}/") for f in files)
        assert any("file1.txt" in f for f in files)
        assert any("file2.txt" in f for f in files)
        assert any("file3.pdf" in f for f in files)

    def test_list_files_with_prefix(self, s3_storage, tmp_path, sample_tenant_id):
        """Test listing files with additional prefix filter."""
        # Upload files with different prefixes
        for i in range(2):
            file_path = tmp_path / f"doc{i}.txt"
            file_path.write_text("Content")
            s3_storage.upload_file(sample_tenant_id, str(file_path), f"docs/doc{i}.txt")

        for i in range(2):
            file_path = tmp_path / f"img{i}.png"
            file_path.write_text("Image")
            s3_storage.upload_file(sample_tenant_id, str(file_path), f"images/img{i}.png")

        # List only docs
        docs = s3_storage.list_files(sample_tenant_id, prefix="docs/")
        assert len(docs) == 2
        assert all("docs/" in f for f in docs)

        # List only images
        images = s3_storage.list_files(sample_tenant_id, prefix="images/")
        assert len(images) == 2
        assert all("images/" in f for f in images)

    def test_list_files_empty_tenant(self, s3_storage):
        """Test listing files for tenant with no files."""
        files = s3_storage.list_files("empty-tenant")
        assert files == []

    def test_tenant_isolation(self, s3_storage, tmp_path):
        """Test that files are properly isolated by tenant."""
        # Upload files for different tenants
        tenant1 = "tenant-1"
        tenant2 = "tenant-2"

        file1 = tmp_path / "tenant1_file.txt"
        file1.write_text("Tenant 1 content")
        s3_storage.upload_file(tenant1, str(file1))

        file2 = tmp_path / "tenant2_file.txt"
        file2.write_text("Tenant 2 content")
        s3_storage.upload_file(tenant2, str(file2))

        # Verify isolation
        tenant1_files = s3_storage.list_files(tenant1)
        tenant2_files = s3_storage.list_files(tenant2)

        assert len(tenant1_files) == 1
        assert len(tenant2_files) == 1
        assert tenant1_files[0].startswith(f"{tenant1}/")
        assert tenant2_files[0].startswith(f"{tenant2}/")

        # Verify tenant 1 cannot see tenant 2's files
        assert not any(tenant2 in f for f in tenant1_files)
        assert not any(tenant1 in f for f in tenant2_files)

    def test_get_file_url(self, s3_storage, sample_tenant_id):
        """Test getting S3 URL for a file."""
        s3_key = f"{sample_tenant_id}/document.pdf"
        url = s3_storage.get_file_url(s3_key)

        assert url == f"s3://{s3_storage.bucket}/{s3_key}"
        assert sample_tenant_id in url
        assert "document.pdf" in url

    def test_upload_and_download_binary_file(self, s3_storage, tmp_path, sample_tenant_id):
        """Test uploading and downloading binary files (like PDFs)."""
        # Create binary content
        binary_content = bytes(range(256))
        upload_file = tmp_path / "binary.bin"
        upload_file.write_bytes(binary_content)

        # Upload
        s3_key = s3_storage.upload_file(sample_tenant_id, str(upload_file))

        # Download
        download_file = tmp_path / "downloaded.bin"
        s3_storage.download_file(s3_key, str(download_file))

        # Verify binary content matches exactly
        assert download_file.read_bytes() == binary_content

    def test_upload_large_file(self, s3_storage, tmp_path, sample_tenant_id):
        """Test uploading a larger file (1MB)."""
        # Create 1MB file
        large_content = b"x" * (1024 * 1024)  # 1MB
        large_file = tmp_path / "large.bin"
        large_file.write_bytes(large_content)

        # Upload
        s3_key = s3_storage.upload_file(sample_tenant_id, str(large_file))

        # Verify
        assert s3_storage.file_exists(s3_key)

        # Download and verify size
        download_file = tmp_path / "large_downloaded.bin"
        s3_storage.download_file(s3_key, str(download_file))
        assert download_file.stat().st_size == 1024 * 1024

    def test_multiple_operations_on_same_file(self, s3_storage, tmp_path, sample_tenant_id):
        """Test multiple operations on the same file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Original content")

        # Upload
        s3_key = s3_storage.upload_file(sample_tenant_id, str(test_file))

        # Verify exists
        assert s3_storage.file_exists(s3_key)

        # Re-upload with updated content (overwrite)
        test_file.write_text("Updated content")
        s3_key2 = s3_storage.upload_file(sample_tenant_id, str(test_file))

        assert s3_key == s3_key2  # Same key

        # Download and verify updated content
        download_file = tmp_path / "downloaded.txt"
        s3_storage.download_file(s3_key, str(download_file))
        assert download_file.read_text() == "Updated content"

        # Delete
        s3_storage.delete_file(s3_key)
        assert not s3_storage.file_exists(s3_key)
