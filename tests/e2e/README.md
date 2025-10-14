# End-to-End (e2e) Tests

End-to-end tests for complete workflow validation with real services.

## Overview

E2E tests validate the entire system working together:

- **Upload** files to S3/MinIO
- **Extract** content from PDFs
- **Generate** embeddings with Cohere
- **Store** in PostgreSQL + pgvector
- **Search** with semantic similarity
- **Generate** RAG-based answers with OpenAI

## Requirements

### Infrastructure

All services must be running:

```bash
# Start infrastructure
docker compose up -d

# Initialize database
task setup-db

# Start ALL Temporal workers
task temporal-all
```

### API Keys

E2E tests require valid API keys:

```bash
# Required for embedding tests
export EMBEDDING_API_KEY=your-cohere-api-key

# Required for LLM tests
export LLM_API_KEY=your-openai-api-key
```

**Without API keys**, tests will be automatically skipped.

## Test Files

### test_full_document_flow.py

**Complete workflow test**: Upload → Extract → Embed → Search → RAG

#### test_full_document_processing_and_search_flow

Tests the complete document processing pipeline:

1. **Upload**: Alice in Wonderland PDF to S3
2. **Extract**: Text, tables, images from PDF
3. **Chunk**: Text into semantic units (sentence-based)
4. **Embed**: Generate embeddings for all chunks (Cohere)
5. **Store**: Save chunks with embeddings to database
6. **Verify**: Check document and chunks were created
7. **Search**: Semantic search with question about characters
8. **Generate**: RAG-based answer with source attribution

**Question Asked**: "Who are the main characters in Alice in Wonderland?"

**Expected Results**:

- Document uploaded successfully
- Chunks created with embeddings
- Semantic search finds relevant chunks
- LLM generates answer mentioning: Alice, White Rabbit, Queen of Hearts, Mad Hatter, Cheshire Cat
- Sources include page numbers and similarity scores

#### test_multi_document_search

Tests searching across multiple documents:

1. Uploads Alice in Wonderland + Frankenstein
2. Processes both documents
3. Searches across both for common themes
4. Generates comparative answer

**Question Asked**: "What are the common themes between these stories?"

**Expected Results**:

- Chunks from both documents in results
- Answer compares themes across books
- Source attribution for both documents

### Other E2E Tests

- `test_extraction.py` - Document extraction workflow
- `test_embedding.py` - Embedding generation workflow
- `test_chunk_embedding.py` - Chunking + embedding workflow
- `test_llm.py` - LLM text generation
- `test_search.py` - Basic search workflow

## Running E2E Tests

### Run All E2E Tests

```bash
# With API keys
export EMBEDDING_API_KEY=your-cohere-key
export LLM_API_KEY=your-openai-key
uv run pytest tests/e2e/ -v
```

### Run Specific Test

```bash
# Full document flow
uv run pytest tests/e2e/test_full_document_flow.py::test_full_document_processing_and_search_flow -v

# Multi-document search
uv run pytest tests/e2e/test_full_document_flow.py::test_multi_document_search -v
```

### Run with Output

```bash
# Show print statements and progress
uv run pytest tests/e2e/test_full_document_flow.py -v -s
```

### Run as Script

```bash
# Run main() function directly
uv run python tests/e2e/test_full_document_flow.py
```

## Test Fixtures

PDF files located in `tests/fixtures/`:

- `alice_in_wonderland_public_domain.pdf` - Lewis Carroll's classic
- `frankenstein_public_domain.pdf` - Mary Shelley's novel
- `moby_dick_public_domain.pdf` - Herman Melville's novel

All fixtures are public domain books.

## Expected Output

### Successful Test Run

```
[1/5] Uploading file to S3...
✓ File uploaded: tenant-abc123/alice_in_wonderland.pdf (156789 bytes)

[2/5] Extracting document and generating embeddings...
✓ Document processed: 550e8400-e29b-41d4-a716-446655440000

[3/5] Verifying document in database...
✓ Document verified: alice_in_wonderland.pdf (status: processed)

[4/5] Verifying chunks with embeddings...
✓ Found 245 chunks

Sample chunks:
  Chunk 1 (page 1): Alice was beginning to get very tired of sitting by her sister...
  Chunk 2 (page 2): There was nothing so very remarkable in that; nor did Alice...
  Chunk 3 (page 3): Down, down, down. Would the fall never come to an end?...

[5/5] Performing semantic search with RAG...

================================================================================
SEARCH RESULTS
================================================================================

Question: Who are the main characters in Alice in Wonderland? List them with brief descriptions.

Answer:
The main characters in Alice in Wonderland include:

1. Alice - A curious young girl who falls down a rabbit hole into Wonderland
2. The White Rabbit - A nervous rabbit always worried about being late
3. The Queen of Hearts - A tyrannical ruler known for ordering executions
4. The Mad Hatter - An eccentric character who hosts a never-ending tea party
5. The Cheshire Cat - A mysterious cat with the ability to appear and disappear

Sources (5 chunks):

1. Document: alice_in_wonderland.pdf
   Page: 12
   Similarity: 0.89
   Content: Alice followed the White Rabbit down the rabbit hole...

2. Document: alice_in_wonderland.pdf
   Page: 45
   Similarity: 0.85
   Content: The Queen of Hearts shouted "Off with their heads!"...

[...]

================================================================================

✓ Answer mentions characters: alice, rabbit, queen, hatter, cheshire
✓ Average similarity score: 0.82

✓ Full e2e test PASSED! All workflow steps completed successfully.
```

## Troubleshooting

### Test Skipped (Missing API Keys)

```
SKIPPED [1] tests/e2e/test_full_document_flow.py:29:
EMBEDDING_API_KEY and LLM_API_KEY required for full e2e test
```

**Solution**: Export API keys before running tests.

### Temporal Connection Error

```
temporalio.client.WorkflowFailureError: Workflow execution failed
```

**Solutions**:

1. Check Temporal server is running: `docker compose ps`
2. Check workers are running: `task temporal-all`
3. Check Temporal UI: http://localhost:8233

### S3 Upload Failed

```
Upload failed: Connection refused
```

**Solutions**:

1. Check MinIO is running: `docker compose ps`
2. Check MinIO logs: `docker compose logs minio`
3. Access MinIO UI: http://localhost:9001

### Database Connection Error

```
asyncpg.exceptions.InvalidCatalogNameError: database "vectordb" does not exist
```

**Solutions**:

1. Check PostgreSQL is running: `docker compose ps`
2. Initialize database: `task setup-db`

### Embedding Generation Failed

```
EmbeddingGenerationError: API key invalid
```

**Solutions**:

1. Check API key is valid
2. Check API key is exported: `echo $EMBEDDING_API_KEY`
3. Verify Cohere account has credits

### Test Takes Too Long

E2E tests can take 2-5 minutes depending on:

- Document size (more pages = longer processing)
- API response times (Cohere + OpenAI)
- Number of chunks generated

**Expected timing**:

- Upload: 5-10 seconds
- Extraction: 30-60 seconds
- Embedding generation: 60-120 seconds (depends on chunk count)
- Search: 10-20 seconds

## Debugging E2E Tests

### Enable Debug Logging

```bash
export GDAI_LOG_LEVEL=DEBUG
uv run pytest tests/e2e/test_full_document_flow.py -v -s
```

### Check Temporal Workflows

Visit Temporal UI: http://localhost:8233

- View workflow execution history
- Check activity logs
- See retry attempts
- View input/output payloads

### Check Database State

```bash
# Connect to database
psql -h localhost -p 5555 -U testuser -d vectordb

# Check documents
SELECT id, tenant_id, name, status FROM documents;

# Check chunks
SELECT document_id, COUNT(*) as chunk_count
FROM chunks
GROUP BY document_id;

# Check embeddings
SELECT COUNT(*) FROM chunks WHERE embedding IS NOT NULL;
```

### Check S3 Files

Access MinIO UI: http://localhost:9001

- Login: minioadmin / minioadmin
- Browse `gdai-documents` bucket
- Check files are uploaded with tenant prefix

## Cost Considerations

E2E tests consume API credits:

### Cohere (Embeddings)

- Alice in Wonderland: ~200-300 chunks
- Cost: ~$0.01-0.02 per test run
- embed-v4.0 model

### OpenAI (LLM)

- Search query: 1 request per test
- Context: 5-10 chunks (~2000-4000 tokens)
- Cost: ~$0.05-0.10 per test run
- GPT-4o model

**Total cost per full test run**: ~$0.06-0.12

## CI/CD Integration

E2E tests are NOT run in CI by default (requires API keys).

To enable in CI:

1. Add secrets to GitHub Actions:
   - `EMBEDDING_API_KEY`
   - `LLM_API_KEY`
2. Update workflow to run e2e tests
3. Consider cost implications for frequent runs

## Related Documentation

- [Testing Strategy](../../.claude/specs/testing.md)
- [Upload File Workflow](../../.claude/specs/upload-file-workflow.md)
- [Extract Document Workflow](../../.claude/specs/extract-document-workflow.md)
- [Embedding Texts Workflow](../../.claude/specs/embedding-texts-workflow.md)
- [Search Documents Workflow](../../.claude/specs/search-documents-workflow.md)
