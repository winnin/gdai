"""End-to-end test for complete document processing and search flow.

This test performs the full workflow:
1. Upload a PDF file to S3
2. Extract document content (text, tables, images)
3. Chunk text into semantic units
4. Generate embeddings for chunks
5. Perform semantic search with a question
6. Generate RAG-based answer with source attribution

Requires:
- Running PostgreSQL + pgvector
- Running MinIO/S3
- Running Temporal server and workers
- EMBEDDING_API_KEY (Cohere)
- LLM_API_KEY (OpenAI)
"""

import os
import time
import uuid
from pathlib import Path

import pytest
from temporalio.client import Client

from gdai.temporal.document_management.schema import GetDocumentChunksInput, GetDocumentInput
from gdai.temporal.extract_document.schema import DocumentExtracInput
from gdai.temporal.extract_document.workflow import DocumentExtractionWorkflow
from gdai.temporal.search_on_documents.schema import SearchInput
from gdai.temporal.upload_file.schema import UploadFileInput
from gdai.temporal.upload_file.workflow import UploadFileWorkflow


def print_step(step_num: int, total_steps: int, description: str, substep: str = ""):
    """Print a formatted step message with optional substep."""
    bar_length = 50
    progress = int((step_num / total_steps) * bar_length)
    bar = "█" * progress + "░" * (bar_length - progress)

    print(f"\n{'=' * 80}")
    print(f"[{step_num}/{total_steps}] {description}")
    print(f"Progress: [{bar}] {int((step_num / total_steps) * 100)}%")
    if substep:
        print(f"    → {substep}")
    print(f"{'=' * 80}")


@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.getenv("EMBEDDING_API_KEY") or not os.getenv("LLM_API_KEY"),
    reason="EMBEDDING_API_KEY and LLM_API_KEY required for full e2e test",
)
async def test_full_document_processing_and_search_flow():
    """Test complete flow: upload → extract → embed → search → RAG answer.

    This test uses Alice in Wonderland PDF and searches for characters.
    """
    # Setup
    tenant_id = f"test-tenant-{uuid.uuid4().hex[:8]}"
    fixture_path = Path(__file__).parent.parent / "fixtures" / "alice_in_wonderland_public_domain.pdf"

    assert fixture_path.exists(), f"Fixture not found: {fixture_path}"

    # Connect to Temporal
    print_step(0, 5, "INITIALIZATION", "Connecting to Temporal and preparing test data")
    print(f"  Tenant ID: {tenant_id}")
    print(f"  Document: {fixture_path.name}")
    client = await Client.connect("localhost:7233")
    print("  ✓ Connected to Temporal")

    # ============================================
    # Step 1: Upload file to S3
    # ============================================
    print_step(1, 5, "UPLOAD FILE TO S3", "Uploading PDF document to MinIO/S3 storage")
    start_time = time.time()

    upload_input = UploadFileInput(
        tenant_id=tenant_id,
        file_path=str(fixture_path),
        object_name="alice_in_wonderland.pdf",
    )

    print("  Starting upload workflow...")
    upload_result = await client.execute_workflow(
        UploadFileWorkflow.run,
        upload_input,
        id=f"upload-{uuid.uuid4()}",
        task_queue="upload-file-queue",
    )

    elapsed = time.time() - start_time
    assert upload_result.success, f"Upload failed: {upload_result.error_message}"
    assert upload_result.s3_key
    assert upload_result.file_size > 0

    print("  ✓ File uploaded successfully!")
    print(f"    S3 Key: {upload_result.s3_key}")
    print(f"    Size: {upload_result.file_size:,} bytes ({upload_result.file_size / 1024 / 1024:.2f} MB)")
    print(f"    Time: {elapsed:.2f}s")

    # ============================================
    # Step 2: Extract document and generate embeddings
    # ============================================
    print_step(2, 5, "EXTRACT DOCUMENT & GENERATE EMBEDDINGS", "Processing PDF and creating vector embeddings")
    start_time = time.time()

    extract_input = DocumentExtracInput(
        s3_key=upload_result.s3_key,
        chunk_strategy="sentence",
        tenant_id=tenant_id,
    )

    print("  Starting document extraction workflow...")
    print("    → Downloading document from S3")
    print("    → Extracting text and metadata")
    print("    → Chunking text into semantic units")
    print("    → Generating embeddings (Cohere)")
    print("    → Storing chunks in database")

    document_id = await client.execute_workflow(
        DocumentExtractionWorkflow.run,
        extract_input,
        id=f"extract-{uuid.uuid4()}",
        task_queue="process-document-queue",
    )

    elapsed = time.time() - start_time
    assert document_id
    print("  ✓ Document extraction completed!")
    print(f"    Document ID: {document_id}")
    print(f"    Time: {elapsed:.2f}s")

    # ============================================
    # Step 3: Verify document was created
    # ============================================
    print_step(3, 5, "VERIFY DOCUMENT IN DATABASE", "Checking document metadata and status")
    start_time = time.time()

    get_doc_input = GetDocumentInput(tenant_id=tenant_id, document_id=document_id)

    print("  Querying document metadata...")
    document = await client.execute_workflow(
        "GetDocumentWorkflow",
        get_doc_input,
        id=f"get-doc-{uuid.uuid4()}",
        task_queue="document-management-queue",
    )

    elapsed = time.time() - start_time
    assert document.id == document_id
    assert document.tenant_id == tenant_id
    assert document.name == "alice_in_wonderland.pdf"
    assert document.status == "processed"
    print("  ✓ Document verified in database!")
    print(f"    Name: {document.name}")
    print(f"    Status: {document.status}")
    print(f"    Tenant: {document.tenant_id}")
    print(f"    Time: {elapsed:.2f}s")

    # ============================================
    # Step 4: Verify chunks were created with embeddings
    # ============================================
    print_step(4, 5, "VERIFY CHUNKS WITH EMBEDDINGS", "Checking chunked text and vector embeddings")
    start_time = time.time()

    get_chunks_input = GetDocumentChunksInput(tenant_id=tenant_id, document_id=document_id)

    print("  Querying document chunks from database...")
    chunks_result = await client.execute_workflow(
        "GetDocumentChunksWorkflow",
        get_chunks_input,
        id=f"get-chunks-{uuid.uuid4()}",
        task_queue="document-management-queue",
    )

    elapsed = time.time() - start_time
    assert chunks_result.total > 0, "No chunks were created"
    print("  ✓ Chunks verified successfully!")
    print(f"    Total chunks: {chunks_result.total}")
    print(f"    Time: {elapsed:.2f}s")

    # Display sample chunks
    print("\n  Sample chunks:")
    for i, chunk in enumerate(chunks_result.chunks[:3]):
        preview = chunk.content[:100].replace("\n", " ")
        print(f"    {i + 1}. Page {chunk.page_number}: {preview}...")

    # ============================================
    # Step 5: Perform semantic search with RAG
    # ============================================
    print_step(5, 5, "SEMANTIC SEARCH WITH RAG", "Searching document and generating AI answer")
    start_time = time.time()

    # Search for characters in Alice in Wonderland
    search_input = SearchInput(
        query_id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        query="Who are the main characters in Alice in Wonderland? List them with brief descriptions.",
        document_ids=[document_id],
        similarity_threshold=0.7,
        max_num_chunks=5,
    )

    print("  Starting semantic search workflow...")
    print("    → Generating query embedding")
    print("    → Vector similarity search (pgvector)")
    print("    → Retrieving relevant chunks")
    print("    → Building context for LLM")
    print("    → Generating answer (OpenAI GPT-4o)")

    search_result = await client.execute_workflow(
        "DocumentSearchWorkflow",
        search_input,
        id=f"search-{uuid.uuid4()}",
        task_queue="search-on-documents-queue",
    )

    elapsed = time.time() - start_time

    # Verify search results
    assert search_result.query == search_input.query
    assert search_result.answer is not None, "No answer was generated"
    assert len(search_result.chunks) > 0, "No relevant chunks found"

    print("  ✓ Search completed successfully!")
    print(f"    Found chunks: {len(search_result.chunks)}")
    print(f"    Answer length: {len(search_result.answer)} characters")
    print(f"    Time: {elapsed:.2f}s")

    # Display results
    print("\n" + "=" * 80)
    print("SEARCH RESULTS")
    print("=" * 80)
    print(f"\nQuestion: {search_result.query}")
    print(f"\nAnswer:\n{search_result.answer}")
    print(f"\n\nSources ({len(search_result.chunks)} chunks):")
    for i, chunk_info in enumerate(search_result.chunks, 1):
        print(f"\n{i}. Document: {document.name}")
        print(f"   Page: {chunk_info.page_number}")
        print(f"   Similarity: {chunk_info.similarity_score:.2f}")
        print(f"   Content: {chunk_info.content[:200]}...")

    print("\n" + "=" * 80)

    # Assertions for answer quality
    assert len(search_result.answer) > 50, "Answer is too short"

    # Check if answer mentions expected characters
    answer_lower = search_result.answer.lower()
    expected_characters = ["alice", "rabbit", "queen", "hatter", "cheshire"]
    found_characters = [char for char in expected_characters if char in answer_lower]

    assert len(found_characters) >= 2, f"Answer should mention at least 2 characters, found: {found_characters}"
    print(f"\n✓ Answer mentions characters: {', '.join(found_characters)}")

    # Verify similarity scores are reasonable
    avg_similarity = sum(c.similarity_score for c in search_result.chunks) / len(search_result.chunks)
    assert avg_similarity >= 0.7, f"Average similarity too low: {avg_similarity:.2f}"
    print(f"✓ Average similarity score: {avg_similarity:.2f}")

    print("\n✓ Full e2e test PASSED! All workflow steps completed successfully.")


@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.getenv("EMBEDDING_API_KEY") or not os.getenv("LLM_API_KEY"),
    reason="EMBEDDING_API_KEY and LLM_API_KEY required for full e2e test",
)
async def test_multi_document_search():
    """Test searching across multiple documents.

    Uploads two different books and searches for common themes.
    """
    tenant_id = f"test-tenant-{uuid.uuid4().hex[:8]}"
    fixtures_dir = Path(__file__).parent.parent / "fixtures"

    # Documents to upload
    documents = [
        ("alice_in_wonderland_public_domain.pdf", "alice"),
        ("frankenstein_public_domain.pdf", "frankenstein"),
    ]

    client = await Client.connect("localhost:7233")
    document_ids = []

    # Upload and process both documents
    for filename, short_name in documents:
        fixture_path = fixtures_dir / filename
        assert fixture_path.exists(), f"Fixture not found: {fixture_path}"

        print(f"\n[Processing {short_name}]")

        # Upload
        upload_input = UploadFileInput(
            tenant_id=tenant_id,
            file_path=str(fixture_path),
            object_name=filename,
        )

        upload_result = await client.execute_workflow(
            UploadFileWorkflow.run,
            upload_input,
            id=f"upload-{short_name}-{uuid.uuid4()}",
            task_queue="upload-file-queue",
        )

        assert upload_result.success
        print(f"✓ Uploaded {short_name}")

        # Extract and embed
        extract_input = DocumentExtracInput(
            s3_key=upload_result.s3_key,
            chunk_strategy="sentence",
            tenant_id=tenant_id,
        )

        document_id = await client.execute_workflow(
            DocumentExtractionWorkflow.run,
            extract_input,
            id=f"extract-{short_name}-{uuid.uuid4()}",
            task_queue="process-document-queue",
        )

        document_ids.append(document_id)
        print(f"✓ Processed {short_name}: {document_id}")

    # Search across both documents
    print("\n[Searching across multiple documents]")
    search_input = SearchInput(
        query_id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        query="What are the common themes between these stories? Compare and contrast the main characters.",
        document_ids=document_ids,
        similarity_threshold=0.7,
        max_num_chunks=10,
    )

    search_result = await client.execute_workflow(
        "DocumentSearchWorkflow",
        search_input,
        id=f"multi-search-{uuid.uuid4()}",
        task_queue="search-on-documents-queue",
    )

    # Verify results
    assert search_result.answer is not None
    assert len(search_result.chunks) > 0

    # Check that chunks come from both documents
    unique_docs = set(c.document_id for c in search_result.chunks)
    assert len(unique_docs) > 1, "Search should return chunks from multiple documents"

    print("\n" + "=" * 80)
    print("MULTI-DOCUMENT SEARCH RESULTS")
    print("=" * 80)
    print(f"\nQuestion: {search_result.query}")
    print(f"\nAnswer:\n{search_result.answer}")
    print(f"\n\nFound chunks from {len(unique_docs)} different documents")

    # Display sources grouped by document
    for doc_id in unique_docs:
        doc_chunks = [c for c in search_result.chunks if c.document_id == doc_id]
        print(f"\n  Document {doc_id[:8]}...: {len(doc_chunks)} chunks")

    print("\n✓ Multi-document search test PASSED!")


if __name__ == "__main__":
    import asyncio

    print("Running full e2e test...")
    print("=" * 80)
    asyncio.run(test_full_document_processing_and_search_flow())
    print("\n\n")
    print("Running multi-document search test...")
    print("=" * 80)
    asyncio.run(test_multi_document_search())
