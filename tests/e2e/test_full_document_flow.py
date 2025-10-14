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
    client = await Client.connect("localhost:7233")

    # ============================================
    # Step 1: Upload file to S3
    # ============================================
    print("\n[1/5] Uploading file to S3...")
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

    assert upload_result.success, f"Upload failed: {upload_result.error_message}"
    assert upload_result.s3_key
    assert upload_result.file_size > 0
    print(f"✓ File uploaded: {upload_result.s3_key} ({upload_result.file_size} bytes)")

    # ============================================
    # Step 2: Extract document and generate embeddings
    # ============================================
    print("\n[2/5] Extracting document and generating embeddings...")
    extract_input = DocumentExtracInput(
        s3_key=upload_result.s3_key,
        chunk_strategy="sentence",
        tenant_id=tenant_id,
    )

    document_id = await client.execute_workflow(
        DocumentExtractionWorkflow.run,
        extract_input,
        id=f"extract-{uuid.uuid4()}",
        task_queue="process-document-queue",
    )

    assert document_id
    print(f"✓ Document processed: {document_id}")

    # ============================================
    # Step 3: Verify document was created
    # ============================================
    print("\n[3/5] Verifying document in database...")
    get_doc_input = GetDocumentInput(tenant_id=tenant_id, document_id=document_id)

    document = await client.execute_workflow(
        "GetDocumentWorkflow",
        get_doc_input,
        id=f"get-doc-{uuid.uuid4()}",
        task_queue="document-management-queue",
    )

    assert document.id == document_id
    assert document.tenant_id == tenant_id
    assert document.name == "alice_in_wonderland.pdf"
    assert document.status == "processed"
    print(f"✓ Document verified: {document.name} (status: {document.status})")

    # ============================================
    # Step 4: Verify chunks were created with embeddings
    # ============================================
    print("\n[4/5] Verifying chunks with embeddings...")
    get_chunks_input = GetDocumentChunksInput(tenant_id=tenant_id, document_id=document_id)

    chunks_result = await client.execute_workflow(
        "GetDocumentChunksWorkflow",
        get_chunks_input,
        id=f"get-chunks-{uuid.uuid4()}",
        task_queue="document-management-queue",
    )

    assert chunks_result.total > 0, "No chunks were created"
    print(f"✓ Found {chunks_result.total} chunks")

    # Display sample chunks
    print("\nSample chunks:")
    for i, chunk in enumerate(chunks_result.chunks[:3]):
        preview = chunk.content[:100].replace("\n", " ")
        print(f"  Chunk {i + 1} (page {chunk.page_number}): {preview}...")

    # ============================================
    # Step 5: Perform semantic search with RAG
    # ============================================
    print("\n[5/5] Performing semantic search with RAG...")

    # Search for characters in Alice in Wonderland
    search_input = SearchInput(
        query_id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        query="Who are the main characters in Alice in Wonderland? List them with brief descriptions.",
        document_ids=[document_id],
        similarity_threshold=0.7,
        top_k=5,
        generate_answer=True,
    )

    search_result = await client.execute_workflow(
        "DocumentSearchWorkflow",
        search_input,
        id=f"search-{uuid.uuid4()}",
        task_queue="search-on-documents-queue",
    )

    # Verify search results
    assert search_result.query == search_input.query
    assert search_result.answer is not None, "No answer was generated"
    assert len(search_result.chunks) > 0, "No relevant chunks found"

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
        top_k=10,
        generate_answer=True,
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
