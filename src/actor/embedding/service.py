"""Module for processing documents through an embedding pipeline."""

from __future__ import annotations

import json
import os

import aiofiles

from src.actor.embedding.repository import DocumentRepository
from src.shared.embedding_model import EmbeddingModel
from src.shared.logger import logger
from src.shared.schema import Document, DocumentChunk


class EmbeddingDocumentService:
    """Service for processing documents through an embedding pipeline."""

    def __init__(
        self,
        embedding_model: EmbeddingModel,
        document_repository: DocumentRepository,
        chunk_size: int = 1000,
        chunk_overlap: int = 50,
    ):
        """Initialize with embedding model, repository, and chunking parameters."""
        self.embedding_model: EmbeddingModel = embedding_model
        self.chunk_size: int = chunk_size
        self.chunk_overlap: int = chunk_overlap
        self.repository = document_repository
        if self.chunk_size <= self.chunk_overlap:
            raise ValueError("Chunk size must be greater than overlap.")

    async def process_document(self, document_path) -> None:
        """Process document: load, chunk, embed, and store in repository."""
        document = await self._load_document(document_path)
        document_chunks = await self._chunk_document(document)
        logger.info(
            f"Document {document.doc_name} has {len(document_chunks)} chunks after processing."
        )
        await self._embed_chunks(document_chunks, self.embedding_model)
        await self.repository.insert_document(document, document_chunks)

    async def _load_document(self, document_path: str) -> Document:
        """Load document from file path and return Document object."""

        if not os.path.exists(document_path):
            raise FileNotFoundError(f"Document file {document_path} does not exist.")
        try:
            async with aiofiles.open(document_path, mode="r") as f:
                contents = await f.read()
        except Exception as e:
            raise FileNotFoundError(
                f"Could not read document file {document_path}: {e}"
            )
        document_data = json.loads(contents)
        document = Document(**document_data)
        return document

    async def _chunk_page(
        self, tenant_id, doc_id, doc_name, page_number, text
    ) -> list[DocumentChunk]:
        page_size = len(text)
        page_chunks = []

        for i in range(0, page_size, self.chunk_size - self.chunk_overlap):
            chunk_text = text[i : i + self.chunk_size]
            chunk_id = f"{tenant_id}_{doc_name}_{doc_id}_{page_number}_{i}"
            chunk = DocumentChunk(
                chunk_id=chunk_id,
                doc_name=doc_name,
                doc_id=doc_id,
                tenant_id=tenant_id,
                chunk_text=chunk_text,
                page_number=page_number,
                begin_offset=i,
                end_offset=i + self.chunk_size,
            )
            page_chunks.append(chunk)
        return page_chunks

    async def _chunk_document_by_paragraph(
        self, tenant_id, doc_id, doc_name, page_number, text
    ) -> list[DocumentChunk]:
        """Split document pages into chunks by paragraphs."""

        page_chunks = []

        paragraphs = text.text.split("\n\n")
        for j, paragraph in enumerate(paragraphs):
            chunk_id = f"{tenant_id}_{doc_name}_{doc_id}_{page_number}_{j}"
            chunk = DocumentChunk(
                chunk_id=chunk_id,
                doc_name=doc_name,
                doc_id=doc_id,
                tenant_id=tenant_id,
                chunk_text=paragraph.strip(),
                page_number=page_number,
                begin_offset=0,  # Adjust as needed
                end_offset=len(paragraph.strip()),  # Adjust as needed
            )
            page_chunks.append(chunk)

        return page_chunks

    async def _chunk_document(
        self, doc: str, chunk_by_paragraph=True
    ) -> list[DocumentChunk]:
        """Split document pages into chunks with specified overlap."""

        page_chunks = []
        num_pages = len(doc.texts)

        if not chunk_by_paragraph:
            for i in range(num_pages):
                page_number = i + 1
                page_chunks.extend(
                    await self._chunk_page(
                        doc.tenant_id,
                        doc.doc_id,
                        doc.doc_name,
                        page_number,
                        doc.texts[i],
                    )
                )

        if chunk_by_paragraph:
            for i in range(num_pages):
                page_number = i + 1
                page_chunks.extend(
                    await self._chunk_document_by_paragraph(
                        doc.tenant_id,
                        doc.doc_id,
                        doc.doc_name,
                        page_number,
                        doc.texts[i],
                    )
                )

        return page_chunks

    async def _embed_chunks(
        self, chunks: list[DocumentChunk], embedding_model: EmbeddingModel
    ) -> None:
        """Generate embeddings for text chunks using the provided model."""

        batch_size = 64
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            texts = [chunk.chunk_text[:1024] for chunk in batch]
            embeddings = await embedding_model.generate_texts_embeddings(texts)
            for chunk, embedding in zip(batch, embeddings, strict=False):
                chunk.embedding = embedding
