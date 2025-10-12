"""Unit tests for document management activities."""

import uuid

import pytest

from gdai.commons.enums import DocumentTypeEnum
from gdai.commons.exceptions import DocumentNotFoundError
from gdai.repositories.models import DocumentModel
from gdai.repositories.pgvector_repository import PGVectorRepository
from gdai.temporal.document_management.activity import (
    delete_document,
    get_document,
    list_documents,
)
from gdai.temporal.document_management.schema import (
    DeleteDocumentInput,
    GetDocumentInput,
    ListDocumentsInput,
)


class TestListDocumentsActivity:
    """Test suite for list_documents activity."""

    @pytest.mark.asyncio
    async def test_list_documents_empty(self, db_session, sample_tenant_id):
        """Test listing documents when tenant has none."""
        input_data = ListDocumentsInput(tenant_id=sample_tenant_id)

        result = await list_documents(input_data)

        assert result.total == 0
        assert result.documents == []

    @pytest.mark.asyncio
    async def test_list_documents_multiple(self, db_session, sample_tenant_id):
        """Test listing multiple documents for a tenant."""
        # Insert test documents
        repo = PGVectorRepository(db_session)

        for i in range(3):
            doc = DocumentModel(
                id=uuid.uuid4(),
                tenant_id=sample_tenant_id,
                name=f"doc{i}.pdf",
                type=DocumentTypeEnum.pdf,
                s3_path=f"{sample_tenant_id}/doc{i}.pdf",
            )
            await repo.insert_document(doc)

        # List documents
        input_data = ListDocumentsInput(tenant_id=sample_tenant_id)
        result = await list_documents(input_data)

        assert result.total == 3
        assert len(result.documents) == 3
        assert all(d.tenant_id == sample_tenant_id for d in result.documents)


class TestGetDocumentActivity:
    """Test suite for get_document activity."""

    @pytest.mark.asyncio
    async def test_get_document_exists(self, db_session, sample_tenant_id):
        """Test getting an existing document."""
        # Insert document
        repo = PGVectorRepository(db_session)
        doc_id = uuid.uuid4()
        doc = DocumentModel(
            id=doc_id,
            tenant_id=sample_tenant_id,
            name="test.pdf",
            type=DocumentTypeEnum.pdf,
            s3_path=f"{sample_tenant_id}/test.pdf",
        )
        await repo.insert_document(doc)

        # Get document
        input_data = GetDocumentInput(tenant_id=sample_tenant_id, document_id=str(doc_id))
        result = await get_document(input_data)

        assert result.id == str(doc_id)
        assert result.name == "test.pdf"
        assert result.s3_path == f"{sample_tenant_id}/test.pdf"

    @pytest.mark.asyncio
    async def test_get_document_not_found(self, db_session, sample_tenant_id):
        """Test getting a nonexistent document."""
        input_data = GetDocumentInput(tenant_id=sample_tenant_id, document_id=str(uuid.uuid4()))

        with pytest.raises(DocumentNotFoundError):
            await get_document(input_data)


class TestDeleteDocumentActivity:
    """Test suite for delete_document activity."""

    @pytest.mark.asyncio
    async def test_delete_document_success(self, db_session, s3_storage, sample_tenant_id, tmp_path):
        """Test successful document deletion from both database and S3."""
        # Create and upload file
        test_file = tmp_path / "delete_me.pdf"
        test_file.write_bytes(b"content")
        s3_key = s3_storage.upload_file(sample_tenant_id, str(test_file))

        # Insert document in database
        repo = PGVectorRepository(db_session)
        doc_id = uuid.uuid4()
        doc = DocumentModel(
            id=doc_id,
            tenant_id=sample_tenant_id,
            name="delete_me.pdf",
            type=DocumentTypeEnum.pdf,
            s3_path=s3_key,
        )
        await repo.insert_document(doc)

        # Verify file exists in S3
        assert s3_storage.file_exists(s3_key)

        # Delete document
        input_data = DeleteDocumentInput(tenant_id=sample_tenant_id, document_id=str(doc_id))
        result = await delete_document(input_data)

        assert result is True

        # Verify deleted from database
        deleted_doc = await repo.get_document(sample_tenant_id, str(doc_id))
        assert deleted_doc is None

        # Verify deleted from S3
        assert not s3_storage.file_exists(s3_key)

    @pytest.mark.asyncio
    async def test_delete_document_not_found(self, db_session, sample_tenant_id):
        """Test deleting a nonexistent document."""
        input_data = DeleteDocumentInput(tenant_id=sample_tenant_id, document_id=str(uuid.uuid4()))

        with pytest.raises(DocumentNotFoundError):
            await delete_document(input_data)

    @pytest.mark.asyncio
    async def test_delete_document_s3_failure_handled(self, db_session, sample_tenant_id):
        """Test that S3 deletion failure doesn't block database deletion."""
        # Insert document with nonexistent S3 path
        repo = PGVectorRepository(db_session)
        doc_id = uuid.uuid4()
        doc = DocumentModel(
            id=doc_id,
            tenant_id=sample_tenant_id,
            name="test.pdf",
            type=DocumentTypeEnum.pdf,
            s3_path="nonexistent/file.pdf",  # Doesn't exist in S3
        )
        await repo.insert_document(doc)

        # Delete should succeed despite S3 failure
        input_data = DeleteDocumentInput(tenant_id=sample_tenant_id, document_id=str(doc_id))
        result = await delete_document(input_data)

        assert result is True

        # Document should be deleted from database
        deleted_doc = await repo.get_document(sample_tenant_id, str(doc_id))
        assert deleted_doc is None
