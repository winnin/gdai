# Extract Document Workflow

Extracts text, tables, and images from PDF documents, chunks the content, generates embeddings, and stores everything in the database.

## Location

`gdai/temporal/extract_document/`

## Temporal Configuration

- **Task Queue**: `process-document-queue`
- **Worker Command**: `task temporal-extract` or `uv run python -m gdai.temporal.extract_document.worker`

## Main Workflow

### DocumentExtractionWorkflow

**Input**: `DocumentExtracInput`

```python
@dataclass
class DocumentExtracInput:
    tenant_id: str           # Tenant identifier
    document_path: str       # S3 key or local path
    chunk_strategy: str      # Chunking strategy ("sentence")
    s3_key: str | None      # S3 key if from S3
```

**Output**: `str` (document_id)

**Workflow Steps**:

1. `_validate_document()` - Validates file exists in S3
2. `_save_document_metadata()` - Saves document to database
3. `_extract_document_content()` - Extracts PDF content (text, tables, images)
4. `_chunk_texts_to_batched_files()` - Chunks text using configured strategy
5. `_get_chunk_file_content_for_embedding()` - Triggers embedding generation (child workflow)
6. `_store_embedded_chunks()` - Stores chunks with embeddings in database
7. `_cleanup_temp_files()` - Removes temporary files

## Activities

### validate

- Validates document exists in S3
- Timeout: 10 seconds

### save_document_metadata

- Creates DocumentModel in database with status "processing"
- Returns document_id
- Timeout: 20 seconds

### extract_document_content

- Downloads PDF from S3 to temp folder
- Extracts text, tables, images using PDFExtractor
- Saves extracted data to temp JSON file
- Returns path to extracted data file
- Timeout: 50 seconds

### chunk_texts_to_batched_files

- Loads extracted data from temp file
- Chunks text using ChunkerFactory (sentence-based)
- Creates ChunkModel instances
- Saves to temp JSON file for embedding
- Returns list of chunk file paths
- Timeout: 50 seconds

### get_chunk_file_content_for_embedding

- Loads chunks from temp file
- Triggers TextEmbeddingWorkflow (child workflow)
- Merges embeddings back into chunks
- Returns chunks with embeddings
- Timeout: 50 seconds

### store_embedded_chunks

- Inserts chunks into database using repository
- Updates document status to "processed"
- Timeout: 50 seconds

### remove_temp_files

- Cleans up temporary extraction and chunk files
- Timeout: 10 seconds

## Child Workflows

Triggers **TextEmbeddingWorkflow** for generating embeddings:

```python
embeddings = await workflow.execute_child_workflow(
    "TextEmbeddingWorkflow",
    content_to_embedding,  # {chunk_id: chunk_text}
    task_queue="embedding-text-queue",
)
```

## Error Handling

- Document status set to "extraction_failed" on extraction errors
- Document status set to "embedding_failed" on embedding errors
- All activities retry 3 times with exponential backoff
- Temporary files cleaned up even on failure

## Integration

Typically called after **UploadFileWorkflow**:

```python
# 1. Upload
upload_result = await UploadFileWorkflow.run(...)

# 2. Extract
document_id = await DocumentExtractionWorkflow.run(
    DocumentExtracInput(
        tenant_id="tenant-1",
        document_path=upload_result.s3_key,
        s3_key=upload_result.s3_key,
        chunk_strategy="sentence"
    )
)
```

## Related Specs

- [Upload File Workflow](./upload-file-workflow.md)
- [Embedding Texts Workflow](./embedding-texts-workflow.md)
- [Services - Extractors](./services.md#extractorspy---document-extraction)
- [Services - Chunkers](./services.md#chunkerspy---text-chunking)
