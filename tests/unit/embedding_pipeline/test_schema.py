from __future__ import annotations

import pytest

from src.actor.embedding_pipeline.schema import Document, DocumentChunk, DocumentInput


class TestSchemaDocumentInput:
    def test_valid_document_input(self):
        input_data = {
            "doc_id": "doc1",
            "tenant_id": "tenant1",
            "doc_name": "Test Document",
            "pages": ["Page 1", "Page 2"],
        }
        document_input = DocumentInput(**input_data)
        assert document_input.doc_id == "doc1"
        assert document_input.doc_name == "Test Document"
        assert document_input.pages == ["Page 1", "Page 2"]

    def test_document_invalid_with_pages_as_string(self):
        input_data = {
            "doc_id": "doc1",
            "tenant_id": "tenant1",
            "doc_name": "Test Document",
            "pages": "Invalid Page",
        }
        with pytest.raises(ValueError):
            DocumentInput(**input_data)

    def test_document_without_doc_id(self):
        input_data = {
            "tenant_id": "tenant1",
            "doc_name": "Test Document",
            "pages": ["Page 1", "Page 2"],
        }
        with pytest.raises(ValueError):
            DocumentInput(**input_data)

    def test_invalid_document_input_without_pages(self):
        input_data = {
            "doc_id": "doc1",
            "tenant_id": "tenant1",
            "doc_name": "Test Document",
        }
        with pytest.raises(ValueError):
            DocumentInput(**input_data)

    def test_tenant_id_minimum_length(self):
        input_data = {
            "doc_id": "doc1",
            "tenant_id": "",
            "doc_name": "Test Document",
            "pages": ["Page 1", "Page 2"],
        }
        with pytest.raises(
            ValueError, match="tenant_id must be between 3 and 256 characters"
        ):
            DocumentInput(**input_data)

    def test_doc_id_minimum_length(self):
        input_data = {
            "doc_id": "",
            "doc_name": "Test Document",
            "pages": ["Page 1", "Page 2"],
        }
        with pytest.raises(
            ValueError, match="doc_id must be between 1 and 128 characters"
        ):
            DocumentInput(**input_data)

    def test_doc_id_maximum_length(self):
        input_data = {
            "doc_id": "d" * 129,
            "doc_name": "Test Document",
            "pages": ["Page 1", "Page 2"],
        }
        with pytest.raises(
            ValueError, match="doc_id must be between 1 and 128 characters"
        ):
            DocumentInput(**input_data)

    def test_doc_name_minimum_length(self):
        input_data = {
            "doc_id": "doc1",
            "doc_name": "",
            "pages": ["Page 1", "Page 2"],
        }
        with pytest.raises(
            ValueError, match="doc_name must be between 1 and 256 characters"
        ):
            DocumentInput(**input_data)

    def test_doc_name_maximum_length(self):
        input_data = {
            "doc_id": "doc1",
            "doc_name": "d" * 257,
            "pages": ["Page 1", "Page 2"],
        }
        with pytest.raises(
            ValueError, match="doc_name must be between 1 and 256 characters"
        ):
            DocumentInput(**input_data)


class TestSchemaDocument:
    def test_valid_document(self):
        document = Document(
            doc_id="doc1",
            tenant_id="tenant1",
            doc_name="Test Document",
            pages=["Page 1", "Page 2"],
            embedding_model_name="test_model",
        )
        assert document.doc_id == "doc1"
        assert document.doc_name == "Test Document"
        assert document.pages == ["Page 1", "Page 2"]
        assert document.embedding_model_name == "test_model"

    def test_invalid_document_without_embedding_model_name(self):
        with pytest.raises(ValueError):
            Document(
                doc_id="doc1",
                tenant_id="tenant1",
                doc_name="Test Document",
                pages=["Page 1", "Page 2"],
            )


class TestSchemaDocumentChunk:
    def test_valid_document_chunk(self):
        chunk = DocumentChunk(
            chunk_id="chunk1",
            tenant_id="tenant1",
            chunk_text="This is a test chunk.",
            page_number=1,
            begin_offset=0,
            end_offset=20,
            doc_id="doc1",
        )
        assert chunk.chunk_id == "chunk1"
        assert chunk.chunk_text == "This is a test chunk."
        assert chunk.page_number == 1
        assert chunk.begin_offset == 0
        assert chunk.end_offset == 20
        assert chunk.doc_id == "doc1"

    def test_invalid_end_offset(self):
        with pytest.raises(
            ValueError, match="end_offset must be greater than or equal to begin_offset"
        ):
            DocumentChunk(
                chunk_id="chunk1",
                tenant_id="tenant1",
                chunk_text="This is a test chunk.",
                page_number=1,
                begin_offset=10,
                end_offset=5,
                doc_id="doc1",
            )

    def test_str_representation(self):
        chunk = DocumentChunk(
            chunk_id="chunk1",
            tenant_id="tenant1",
            chunk_text="This is a test chunk.",
            page_number=1,
            begin_offset=0,
            end_offset=20,
            doc_id="doc1",
        )
        assert (
            str(chunk)
            == "DocumentChunk(chunk_id=chunk1, page_number=1, offsets=(0, 20))"
        )
