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


def print_step_start(step_num: int, description: str):
    """Print when a step starts."""
    print(f"\n{'=' * 80}")
    print(f"[Step {step_num}] {description}")
    print(f"{'=' * 80}")
    print(f"⏳ Starting step {step_num}...")


def print_step_complete(step_num: int, elapsed: float, details: dict = None):
    """Print when a step completes."""
    print(f"✓ Step {step_num} completed in {elapsed:.2f}s")
    if details:
        for key, value in details.items():
            print(f"  {key}: {value}")
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

    # Display all steps upfront
    print("\n" + "=" * 80)
    print("END-TO-END DOCUMENT PROCESSING TEST")
    print("=" * 80)
    print(f"\nTenant ID: {tenant_id}")
    print(f"Document: {fixture_path.name}")
    print("\nTest Steps:")
    print("  1. Upload file to S3/MinIO storage")
    print("  2. Extract document and generate embeddings")
    print("  3. Verify document metadata in database")
    print("  4. Verify chunks with embeddings were created")
    print("  5. Perform semantic search with RAG")
    print("=" * 80)

    # Connect to Temporal
    print("\n⏳ Connecting to Temporal...")
    client = await Client.connect("localhost:7233")
    print("✓ Connected to Temporal")

    # ============================================
    # Step 1: Upload file to S3
    # ============================================
    print_step_start(1, "UPLOAD FILE TO S3")
    start_time = time.time()

    upload_input = UploadFileInput(
        tenant_id=tenant_id,
        file_path=str(fixture_path),
        object_name="alice_in_wonderland.pdf",
    )

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

    print_step_complete(
        1,
        elapsed,
        {
            "S3 Key": upload_result.s3_key,
            "File Size": f"{upload_result.file_size:,} bytes ({upload_result.file_size / 1024 / 1024:.2f} MB)",
        },
    )

    # ============================================
    # Step 2: Extract document and generate embeddings
    # ============================================
    print_step_start(2, "EXTRACT DOCUMENT & GENERATE EMBEDDINGS")
    start_time = time.time()

    extract_input = DocumentExtracInput(
        s3_key=upload_result.s3_key,
        chunk_strategy="sentence",
        tenant_id=tenant_id,
    )

    print("  → Downloading document from S3")
    print("  → Extracting text and metadata")
    print("  → Chunking text into semantic units")
    print("  → Generating embeddings (Cohere)")
    print("  → Storing chunks in database")

    document_id = await client.execute_workflow(
        DocumentExtractionWorkflow.run,
        extract_input,
        id=f"extract-{uuid.uuid4()}",
        task_queue="process-document-queue",
    )

    elapsed = time.time() - start_time
    assert document_id
    print_step_complete(2, elapsed, {"Document ID": document_id})

    # ============================================
    # Step 3: Verify document was created
    # ============================================
    print_step_start(3, "VERIFY DOCUMENT IN DATABASE")
    start_time = time.time()

    get_doc_input = GetDocumentInput(tenant_id=tenant_id, document_id=document_id)

    document = await client.execute_workflow(
        "GetDocumentWorkflow",
        get_doc_input,
        id=f"get-doc-{uuid.uuid4()}",
        task_queue="document-management-queue",
    )

    elapsed = time.time() - start_time
    assert document["id"] == document_id
    assert document["name"] == "alice_in_wonderland.pdf"
    assert document["status"] == "processed"
    assert document["type"] == "pdf"
    assert document["s3_path"] == upload_result.s3_key
    assert document["chunk_strategy"] == "sentence"

    print_step_complete(
        3,
        elapsed,
        {
            "Name": document["name"],
            "Status": document["status"],
            "Type": document["type"],
            "Chunk Strategy": document["chunk_strategy"],
        },
    )

    # ============================================
    # Step 4: Verify chunks were created with embeddings
    # ============================================
    print_step_start(4, "VERIFY CHUNKS WITH EMBEDDINGS")
    start_time = time.time()

    get_chunks_input = GetDocumentChunksInput(tenant_id=tenant_id, document_id=document_id)

    chunks_result = await client.execute_workflow(
        "GetDocumentChunksWorkflow",
        get_chunks_input,
        id=f"get-chunks-{uuid.uuid4()}",
        task_queue="document-management-queue",
    )

    elapsed = time.time() - start_time
    assert chunks_result["total"] > 0, "No chunks were created"

    print_step_complete(4, elapsed, {"Total chunks": chunks_result["total"]})

    # Display sample chunks
    print("\nSample chunks:")
    for i, chunk in enumerate(chunks_result["chunks"][:3]):
        preview = chunk["chunk"][:100].replace("\n", " ")
        print(f"  {i + 1}. Page {chunk['page_number']}: {preview}...")

    # ============================================
    # Step 5: Perform semantic search with RAG
    # ============================================
    print_step_start(5, "SEMANTIC SEARCH WITH RAG")
    start_time = time.time()

    # Search for characters in Alice in Wonderland
    search_input = SearchInput(
        query_id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        query="Who are the main characters in Alice in Wonderland? List them with brief descriptions.",
        document_ids=[document_id],
        similarity_threshold=0.2,
        max_num_chunks=100,
    )

    print("  → Generating query embedding")
    print("  → Vector similarity search (pgvector)")
    print("  → Retrieving relevant chunks")
    print("  → Building context for LLM")
    print("  → Generating answer (OpenAI GPT-4o)")

    search_result = await client.execute_workflow(
        "DocumentSearchWorkflow",
        search_input,
        id=f"search-{uuid.uuid4()}",
        task_queue="search-on-documents-queue",
    )

    elapsed = time.time() - start_time

    # Verify search results
    assert search_result["query"] == search_input.query
    assert search_result["answer"] is not None, "No answer was generated"
    assert len(search_result["chunks"]) > 0, "No relevant chunks found"

    print_step_complete(
        5,
        elapsed,
        {
            "Found chunks": len(search_result["chunks"]),
            "Answer length": f"{len(search_result['answer'])} characters",
        },
    )

    # Display results
    print("\n" + "=" * 80)
    print("SEARCH RESULTS")
    print("=" * 80)
    print(f"\nQuestion: {search_result['query']}")
    print(f"\nAnswer:\n{search_result['answer']}")
    print(f"\n\nSources ({len(search_result['chunks'])} chunks):")
    for i, chunk_info in enumerate(search_result["chunks"], 1):
        print(f"\n{i}. Document: {document['name']}")
        print(f"   Page: {chunk_info['page_number']}")
        print(f"   Similarity: {chunk_info['query_similarity']:.2f}")
        print(f"   Content: {chunk_info['text'][:200]}...")

    print("\n" + "=" * 80)

    # Assertions for answer quality
    assert len(search_result["answer"]) > 50, "Answer is too short"

    # Check if answer mentions expected characters
    answer_lower = search_result["answer"].lower()
    expected_characters = ["alice", "rabbit", "queen", "hatter", "cheshire"]
    found_characters = [char for char in expected_characters if char in answer_lower]

    assert len(found_characters) >= 2, f"Answer should mention at least 2 characters, found: {found_characters}"
    print(f"\n✓ Answer mentions characters: {', '.join(found_characters)}")

    # Display similarity scores
    avg_similarity = sum(c["query_similarity"] for c in search_result["chunks"]) / len(search_result["chunks"])
    print(f"✓ Average similarity score: {avg_similarity:.2f}")

    print("\n✓ Full e2e test PASSED! All workflow steps completed successfully.")


if __name__ == "__main__":
    import asyncio

    print("Running full e2e test...")
    print("=" * 80)
    asyncio.run(test_full_document_processing_and_search_flow())
