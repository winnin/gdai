# Upload File Workflow

This workflow handles file upload operations to S3/MinIO storage with multi-tenant isolation.

## Location

`gdai/temporal/upload_file/`

## Overview

The Upload File module provides Temporal workflows and activities for managing files in S3-compatible object storage. It supports uploading files from local disk, uploading in-memory file objects, deleting files, checking file existence, and listing files per tenant.

## Temporal Configuration

- **Task Queue**: `upload-file-queue`
- **Worker Command**: `task temporal-upload` or `uv run python -m gdai.temporal.upload_file.worker`
- **Namespace**: `default` (configurable via `TEMPORAL_NAMESPACE`)

## Workflows

### UploadFileWorkflow

Uploads a file from local disk to S3.

**Workflow Definition**: `@workflow.defn class UploadFileWorkflow`

**Input**: `UploadFileInput`

```python
@dataclass
class UploadFileInput:
    tenant_id: str                      # Tenant identifier for isolation
    file_path: str                      # Local path to file
    object_name: str | None = None     # Optional custom S3 object name
    metadata: dict[str, str] | None = None  # Optional file metadata
```

**Output**: `UploadFileOutput`

```python
@dataclass
class UploadFileOutput:
    s3_key: str           # S3 key (tenant_id/filename)
    s3_url: str           # Full S3 URL
    file_size: int        # File size in bytes
    success: bool         # Upload success status
    error_message: str | None = None  # Error message if failed
```

**Workflow Execution**:

1. Validates input parameters
2. Executes `upload_file` activity
3. Returns upload result with S3 key and URL

**Timeout & Retry Policy**:

- **Schedule-to-close timeout**: 5 minutes
- **Retry policy**:
  - Maximum attempts: 3
  - Initial interval: 1 second
  - Maximum interval: 10 seconds
  - Backoff coefficient: 2.0

**Usage Example**:

```python
from temporalio.client import Client
from gdai.temporal.upload_file.schema import UploadFileInput
from gdai.temporal.upload_file.workflow import UploadFileWorkflow

client = await Client.connect("localhost:7233")

result = await client.execute_workflow(
    UploadFileWorkflow.run,
    UploadFileInput(
        tenant_id="tenant-123",
        file_path="/path/to/document.pdf",
        object_name="document.pdf"
    ),
    id=f"upload-file-{uuid.uuid4()}",
    task_queue="upload-file-queue",
)

print(f"File uploaded to: {result.s3_url}")
```

---

### UploadFileobjWorkflow

Uploads an in-memory file object (bytes) to S3.

**Workflow Definition**: `@workflow.defn class UploadFileobjWorkflow`

**Input**: `UploadFileobjInput`

```python
@dataclass
class UploadFileobjInput:
    tenant_id: str                     # Tenant identifier
    file_content: bytes                # File content as bytes
    object_name: str                   # S3 object name
    content_type: str | None = None   # MIME type
    metadata: dict[str, str] | None = None  # Optional metadata
```

**Output**: `UploadFileOutput` (same as UploadFileWorkflow)

**Workflow Execution**:

1. Validates input parameters
2. Executes `upload_fileobj` activity
3. Returns upload result

**Timeout & Retry Policy**: Same as UploadFileWorkflow

**Use Case**: Uploading files that are already in memory (e.g., from HTTP uploads, generated files).

---

### DeleteFileWorkflow

Deletes a file from S3.

**Workflow Definition**: `@workflow.defn class DeleteFileWorkflow`

**Input**: `DeleteFileInput`

```python
@dataclass
class DeleteFileInput:
    s3_key: str  # S3 key of file to delete
```

**Output**: `DeleteFileOutput`

```python
@dataclass
class DeleteFileOutput:
    s3_key: str           # S3 key that was deleted
    success: bool         # Deletion success status
    error_message: str | None = None  # Error if failed
```

**Workflow Execution**:

1. Validates S3 key
2. Executes `delete_file` activity
3. Returns deletion result

**Timeout & Retry Policy**:

- **Schedule-to-close timeout**: 30 seconds
- **Retry policy**: Same as UploadFileWorkflow

**Note**: This does NOT delete the document from the database. Use `DeleteDocumentWorkflow` from document_management module for complete deletion.

---

### CheckFileExistsWorkflow

Checks if a file exists in S3.

**Workflow Definition**: `@workflow.defn class CheckFileExistsWorkflow`

**Input**: `CheckFileExistsInput`

```python
@dataclass
class CheckFileExistsInput:
    s3_key: str  # S3 key to check
```

**Output**: `CheckFileExistsOutput`

```python
@dataclass
class CheckFileExistsOutput:
    s3_key: str   # S3 key that was checked
    exists: bool  # Whether file exists
```

**Workflow Execution**:

1. Executes `check_file_exists` activity
2. Returns existence status

**Timeout**: 30 seconds (no retry policy - read-only operation)

---

### ListFilesWorkflow

Lists all files for a tenant in S3.

**Workflow Definition**: `@workflow.defn class ListFilesWorkflow`

**Input**: `ListFilesInput`

```python
@dataclass
class ListFilesInput:
    tenant_id: str         # Tenant identifier
    prefix: str = ""       # Optional prefix filter within tenant namespace
```

**Output**: `ListFilesOutput`

```python
@dataclass
class ListFilesOutput:
    files: list[FileInfo]  # List of file information
    total: int             # Total number of files

@dataclass
class FileInfo:
    s3_key: str           # S3 key
    size: int             # File size in bytes
    last_modified: str    # Last modification timestamp (ISO format)
```

**Workflow Execution**:

1. Executes `list_files` activity
2. Returns list of files with metadata

**Timeout**: 2 minutes

---

## Activities

All activities are async functions decorated with `@activity.defn`.

### upload_file

**Function**: `async def upload_file(input: UploadFileInput) -> UploadFileOutput`

**Purpose**: Uploads a file from local disk to S3 with tenant isolation.

**Steps**:

1. Validates file exists on disk
2. Gets file size
3. Calls `S3StorageService.upload_file()`
4. Generates S3 URL
5. Returns result

**Error Handling**:

- Returns `UploadFileOutput` with `success=False` and error message
- Never raises exceptions (returns structured errors)

### upload_fileobj

**Function**: `async def upload_fileobj(input: UploadFileobjInput) -> UploadFileOutput`

**Purpose**: Uploads in-memory file object to S3.

**Steps**:

1. Gets file size from bytes
2. Creates `io.BytesIO` object
3. Calls `S3StorageService.upload_fileobj()`
4. Generates S3 URL
5. Returns result

**Error Handling**: Same as `upload_file`

### delete_file

**Function**: `async def delete_file(input: DeleteFileInput) -> DeleteFileOutput`

**Purpose**: Deletes a file from S3.

**Steps**:

1. Calls `S3StorageService.delete_file()`
2. Returns result

**Error Handling**: Returns structured errors

### check_file_exists

**Function**: `async def check_file_exists(input: CheckFileExistsInput) -> CheckFileExistsOutput`

**Purpose**: Checks if a file exists in S3.

**Steps**:

1. Calls `S3StorageService.file_exists()`
2. Returns existence status

**Error Handling**: Raises exceptions (read-only, no side effects)

### list_files

**Function**: `async def list_files(input: ListFilesInput) -> ListFilesOutput`

**Purpose**: Lists all files for a tenant with optional prefix filter.

**Steps**:

1. Calls `S3StorageService.list_files()`
2. Gets metadata for each file (size, last modified)
3. Returns list of `FileInfo` objects

**Error Handling**: Raises exceptions (read-only operation)

---

## Multi-Tenant Isolation

All file operations enforce tenant isolation:

**S3 Key Format**: `{tenant_id}/{filename}`

Example:

```
s3://gdai-documents/
  ├── tenant-1/
  │   ├── document1.pdf
  │   └── document2.pdf
  └── tenant-2/
      └── document3.pdf
```

**Isolation Guarantees**:

- Upload: File stored with tenant prefix
- List: Only files with tenant prefix returned
- Delete: Requires full S3 key (includes tenant prefix)
- Exists: Checks specific S3 key (includes tenant prefix)

---

## Integration with Other Workflows

### Extract Document Workflow

After uploading a file, typically the Extract Document Workflow is triggered:

```python
# 1. Upload file
upload_result = await client.execute_workflow(
    UploadFileWorkflow.run,
    UploadFileInput(tenant_id="tenant-1", file_path="doc.pdf"),
    task_queue="upload-file-queue",
)

# 2. Extract document
extract_result = await client.execute_workflow(
    DocumentExtractionWorkflow.run,
    DocumentExtractInput(
        tenant_id="tenant-1",
        s3_key=upload_result.s3_key,
        chunk_strategy="sentence"
    ),
    task_queue="process-document-queue",
)
```

### Delete Document Workflow

When deleting a document, both database records AND S3 files are deleted:

```python
# Document Management Workflow handles both:
# 1. Delete from database (document + chunks)
# 2. Delete from S3 (calls DeleteFileWorkflow internally)
await client.execute_workflow(
    DeleteDocumentWorkflow.run,
    DeleteDocumentInput(tenant_id="tenant-1", document_id=doc_id),
    task_queue="document-management-queue",
)
```

---

## Worker

**File**: `worker.py`

**Start Command**:

```bash
task temporal-upload
# or
uv run python -m gdai.temporal.upload_file.worker
```

**Registered Activities**:

- `upload_file`
- `upload_fileobj`
- `delete_file`
- `check_file_exists`
- `list_files`

**Registered Workflows**:

- `UploadFileWorkflow`
- `UploadFileobjWorkflow`
- `DeleteFileWorkflow`
- `CheckFileExistsWorkflow`
- `ListFilesWorkflow`

**Task Queue**: `upload-file-queue`

---

## Error Handling

### Activity Errors

Activities return structured errors rather than raising exceptions:

```python
UploadFileOutput(
    s3_key="",
    s3_url="",
    file_size=0,
    success=False,
    error_message="File not found: /path/to/file.pdf"
)
```

### Workflow Errors

Workflows catch activity exceptions and return error outputs:

```python
try:
    result = await workflow.execute_activity("upload_file", input, ...)
    return result
except Exception as e:
    return UploadFileOutput(
        s3_key="", s3_url="", file_size=0,
        success=False, error_message=str(e)
    )
```

### Retry Behavior

- **Automatic retries**: 3 attempts with exponential backoff
- **Idempotent operations**: Upload operations are idempotent (overwrite if exists)
- **Read operations**: No retry (CheckFileExists, ListFiles)

---

## Configuration

Uses `S3Settings` from commons:

```bash
# Environment Variables
S3_ENDPOINT=http://localhost:9000        # MinIO/S3 endpoint
S3_ACCESS_KEY=minioadmin                 # Access key
S3_SECRET_KEY=minioadmin                 # Secret key
S3_BUCKET=gdai-documents                 # Bucket name
S3_REGION=us-east-1                      # Region
S3_USE_SSL=false                         # Use SSL (true for AWS)
```

---

## Testing

### Integration Tests

**File**: `tests/integration/test_upload_file_workflow.py`

**Tests**:

- `test_upload_file_activity` - Test file upload from disk
- `test_upload_fileobj_activity` - Test in-memory file upload
- `test_delete_file_activity` - Test file deletion
- `test_check_file_exists_activity` - Test existence check
- `test_list_files_activity` - Test file listing
- `test_upload_file_workflow_end_to_end` - Test complete workflow
- `test_multi_tenant_isolation` - Test tenant isolation

**Requirements**:

- Running MinIO/S3 instance
- PostgreSQL not required (this module is storage-only)

---

## Related Specifications

- [Overview](./overview.md) - Project overview
- [Services - S3 Storage](./services.md#s3_storagepy---object-storage) - S3 service implementation
- [Extract Document Workflow](./extract-document-workflow.md) - Uses uploaded files
- [Document Management Workflow](./document-management-workflow.md) - Manages document lifecycle including deletion
