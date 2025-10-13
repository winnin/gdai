# Document Management Workflow

Provides CRUD operations for documents including listing, retrieving, deleting documents and getting document chunks.

## Location

`gdai/temporal/document_management/`

## Temporal Configuration

- **Task Queue**: `document-management-queue`
- **Worker Command**: `task temporal-document` or `uv run python -m gdai.temporal.document_management.worker`

## Workflows

### ListDocumentsWorkflow

Lists all documents for a tenant.

**Input**: `ListDocumentsInput`

```python
@dataclass
class ListDocumentsInput:
    tenant_id: str
```

**Output**: `ListDocumentsOutput`

```python
@dataclass
class ListDocumentsOutput:
    documents: list[Document]
    total: int

@dataclass
class Document:
    id: str
    name: str
    type: str
    status: str
    s3_path: str
    created_at: str
    updated_at: str
```

**Activity**: `list_documents`

---

### GetDocumentWorkflow

Retrieves a specific document by ID.

**Input**: `GetDocumentInput`

```python
@dataclass
class GetDocumentInput:
    tenant_id: str
    document_id: str
```

**Output**: `Document`

**Activity**: `get_document`

**Errors**: Raises `DocumentNotFoundError` if document doesn't exist

---

### DeleteDocumentWorkflow

Deletes a document, its chunks, and the S3 file.

**Input**: `DeleteDocumentInput`

```python
@dataclass
class DeleteDocumentInput:
    tenant_id: str
    document_id: str
```

**Output**: `None`

**Activity**: `delete_document`

**Steps**:

1. Get document from database
2. Delete from S3 using DeleteFileWorkflow
3. Delete chunks from database
4. Delete document from database

**Cascade**: Automatically deletes all associated chunks

---

### GetDocumentChunksWorkflow

Retrieves all chunks for a document.

**Input**: `GetDocumentChunksInput`

```python
@dataclass
class GetDocumentChunksInput:
    tenant_id: str
    document_id: str
```

**Output**: `GetDocumentChunksOutput`

```python
@dataclass
class GetDocumentChunksOutput:
    chunks: list[Chunk]
    total: int

@dataclass
class Chunk:
    id: str
    document_id: str
    content: str
    type: str
    page_number: int
    created_at: str
```

**Activity**: `get_document_chunks`

---

### GetDocumentStatusWorkflow

Gets document processing status.

**Input**: `GetDocumentStatusInput`

```python
@dataclass
class GetDocumentStatusInput:
    tenant_id: str
    document_id: str
```

**Output**: `DocumentStatus`

```python
@dataclass
class DocumentStatus:
    document_id: str
    status: str
    total_chunks: int
    chunks_with_embeddings: int
    processing_complete: bool
```

**Activity**: `get_document_status`

**Use Case**: Track document processing progress

---

## Activities

### list_documents

- Queries PGVectorRepository for all documents
- Filters by tenant_id
- Returns ordered by created_at DESC
- Timeout: 30 seconds

### get_document

- Queries single document by ID
- Validates tenant ownership
- Raises DocumentNotFoundError if not found
- Timeout: 15 seconds

### delete_document

- Retrieves document metadata
- Calls DeleteFileWorkflow to remove S3 file
- Deletes chunks (cascade)
- Deletes document record
- Timeout: 2 minutes

### get_document_chunks

- Queries all chunks for document
- Returns with page number ordering
- Includes embeddings if requested
- Timeout: 1 minute

### get_document_status

- Gets document record
- Counts total chunks
- Counts chunks with embeddings
- Determines if processing complete
- Timeout: 20 seconds

---

## Multi-Tenant Isolation

All workflows enforce tenant isolation:

- All queries filter by `tenant_id`
- Attempting to access another tenant's documents raises `DocumentNotFoundError`
- S3 file deletion uses tenant-prefixed keys

---

## Integration

### With Upload & Extract Workflows

```python
# 1. Upload file
upload_result = await UploadFileWorkflow.run(...)

# 2. Extract document
doc_id = await DocumentExtractionWorkflow.run(...)

# 3. Get document status (check progress)
status = await GetDocumentStatusWorkflow.run(
    GetDocumentStatusInput(tenant_id="tenant-1", document_id=doc_id)
)

# 4. List all documents
docs = await ListDocumentsWorkflow.run(
    ListDocumentsInput(tenant_id="tenant-1")
)

# 5. Delete document when done
await DeleteDocumentWorkflow.run(
    DeleteDocumentInput(tenant_id="tenant-1", document_id=doc_id)
)
```

---

## Error Handling

- `DocumentNotFoundError` - Document doesn't exist or wrong tenant
- `DocumentAlreadyExistsError` - Duplicate document (not used in these workflows)
- All activities retry 3 times with exponential backoff
- Delete operations are idempotent (safe to retry)

---

## Related Specs

- [Upload File Workflow](./upload-file-workflow.md) - Uploads files before extraction
- [Extract Document Workflow](./extract-document-workflow.md) - Creates documents and chunks
- [Search Documents Workflow](./search-documents-workflow.md) - Searches document chunks
- [Repositories](./repositories.md) - Data access layer
