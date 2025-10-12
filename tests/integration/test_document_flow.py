"""Integration tests for complete document processing flow."""

import uuid

import pytest

from gdai.repositories import RepositoryFactory


class TestDocumentProcessingFlow:
    """Integration tests for end-to-end document processing."""

    @pytest.mark.asyncio
    async def test_upload_and_store_document(self, s3_storage, db_session, sample_pdf_path, sample_tenant_id):
        """Test complete flow: upload to S3 -> save metadata -> verify."""
        # Step 1: Upload to S3
        s3_key = s3_storage.upload_file(sample_tenant_id, str(sample_pdf_path))

        assert s3_storage.file_exists(s3_key)
        assert s3_key.startswith(f"{sample_tenant_id}/")

        # Step 2: Save document metadata
        from gdai.commons.enums import DocumentTypeEnum
        from gdai.repositories.models import DocumentModel

        repo = RepositoryFactory.get_repository()

        doc_id = uuid.uuid4()
        doc = DocumentModel(
            id=doc_id,
            tenant_id=sample_tenant_id,
            name=sample_pdf_path.name,
            type=DocumentTypeEnum.pdf,
            s3_path=s3_key,
        )

        await repo.insert_document(doc)

        # Step 3: Verify document is retrievable
        retrieved_doc = await repo.get_document(sample_tenant_id, str(doc_id))

        assert retrieved_doc is not None
        assert retrieved_doc.id == doc_id
        assert retrieved_doc.s3_path == s3_key

        # Step 4: Verify file is downloadable from S3
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            download_path = Path(tmpdir) / "downloaded.pdf"
            s3_storage.download_file(s3_key, str(download_path))

            assert download_path.exists()
            assert download_path.stat().st_size > 0

    @pytest.mark.asyncio
    async def test_document_deletion_flow(self, s3_storage, db_session, sample_pdf_path, sample_tenant_id):
        """Test complete deletion flow: create -> delete from DB and S3."""
        # Create document
        s3_key = s3_storage.upload_file(sample_tenant_id, str(sample_pdf_path))

        from gdai.commons.enums import DocumentTypeEnum
        from gdai.repositories.models import DocumentModel

        repo = RepositoryFactory.get_repository()

        doc_id = uuid.uuid4()
        doc = DocumentModel(
            id=doc_id,
            tenant_id=sample_tenant_id,
            name="test.pdf",
            type=DocumentTypeEnum.pdf,
            s3_path=s3_key,
        )

        await repo.insert_document(doc)

        # Verify exists
        assert await repo.get_document(sample_tenant_id, str(doc_id)) is not None
        assert s3_storage.file_exists(s3_key)

        # Delete document
        await repo.delete_document(sample_tenant_id, str(doc_id))
        s3_storage.delete_file(s3_key)

        # Verify deleted
        assert await repo.get_document(sample_tenant_id, str(doc_id)) is None
        assert not s3_storage.file_exists(s3_key)

    @pytest.mark.asyncio
    async def test_multi_tenant_isolation(self, s3_storage, db_session, sample_pdf_path):
        """Test that documents are isolated between tenants."""
        tenant1 = "tenant-1"
        tenant2 = "tenant-2"

        # Upload for tenant 1
        s3_key1 = s3_storage.upload_file(tenant1, str(sample_pdf_path), "doc1.pdf")

        # Upload for tenant 2
        s3_key2 = s3_storage.upload_file(tenant2, str(sample_pdf_path), "doc2.pdf")

        # Create documents in DB
        from gdai.commons.enums import DocumentTypeEnum
        from gdai.repositories.models import DocumentModel

        repo = RepositoryFactory.get_repository()

        doc1 = DocumentModel(
            id=uuid.uuid4(),
            tenant_id=tenant1,
            name="doc1.pdf",
            type=DocumentTypeEnum.pdf,
            s3_path=s3_key1,
        )

        doc2 = DocumentModel(
            id=uuid.uuid4(),
            tenant_id=tenant2,
            name="doc2.pdf",
            type=DocumentTypeEnum.pdf,
            s3_path=s3_key2,
        )

        await repo.insert_document(doc1)
        await repo.insert_document(doc2)

        # Verify isolation in DB
        tenant1_docs = await repo.get_all_documents(tenant1)
        tenant2_docs = await repo.get_all_documents(tenant2)

        assert len(tenant1_docs) == 1
        assert len(tenant2_docs) == 1
        assert tenant1_docs[0].tenant_id == tenant1
        assert tenant2_docs[0].tenant_id == tenant2

        # Verify isolation in S3
        tenant1_files = s3_storage.list_files(tenant1)
        tenant2_files = s3_storage.list_files(tenant2)

        assert len(tenant1_files) == 1
        assert len(tenant2_files) == 1
        assert s3_key1 in tenant1_files
        assert s3_key2 in tenant2_files
