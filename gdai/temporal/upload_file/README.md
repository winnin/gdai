# File Upload Workflows

This module provides Temporal workflows for managing file uploads to S3/MinIO storage with multi-tenant isolation.

## Features

- **File Upload from Local Path**: Upload files from local filesystem to S3
- **File Upload from Memory**: Upload file objects (bytes) directly to S3
- **File Deletion**: Delete files from S3 storage
- **File Existence Check**: Verify if a file exists in S3
- **List Files**: List all files for a tenant with optional prefix filtering

## Workflows

### UploadFileWorkflow

Upload a file from local filesystem to S3 with automatic tenant isolation.

**Input:**

```python
UploadFileInput(
    tenant_id="my-tenant",
    file_path="/path/to/local/file.pdf",
    object_name="document.pdf",  # Optional, defaults to filename
    metadata={"key": "value"}     # Optional
)
```

**Output:**

```python
UploadFileOutput(
    s3_key="my-tenant/document.pdf",
    s3_url="s3://bucket/my-tenant/document.pdf",
    file_size=12345,
    success=True,
    error_message=None
)
```

### UploadFileobjWorkflow

Upload file content from memory (bytes) to S3.

**Input:**

```python
UploadFileobjInput(
    tenant_id="my-tenant",
    file_content=b"File content as bytes",
    object_name="document.txt",
    content_type="text/plain",    # Optional
    metadata={"key": "value"}     # Optional
)
```

**Output:**

```python
UploadFileOutput(
    s3_key="my-tenant/document.txt",
    s3_url="s3://bucket/my-tenant/document.txt",
    file_size=21,
    success=True,
    error_message=None
)
```

### DeleteFileWorkflow

Delete a file from S3 storage.

**Input:**

```python
DeleteFileInput(
    s3_key="my-tenant/document.pdf"
)
```

**Output:**

```python
DeleteFileOutput(
    s3_key="my-tenant/document.pdf",
    success=True,
    error_message=None
)
```

### CheckFileExistsWorkflow

Check if a file exists in S3.

**Input:**

```python
CheckFileExistsInput(
    s3_key="my-tenant/document.pdf"
)
```

**Output:**

```python
CheckFileExistsOutput(
    s3_key="my-tenant/document.pdf",
    exists=True
)
```

### ListFilesWorkflow

List all files for a tenant in S3.

**Input:**

```python
ListFilesInput(
    tenant_id="my-tenant",
    prefix="subdir/"  # Optional prefix filter
)
```

**Output:**

```python
ListFilesOutput(
    files=[
        FileInfo(
            s3_key="my-tenant/file1.pdf",
            size=12345,
            last_modified="2024-01-01T00:00:00"
        ),
        FileInfo(
            s3_key="my-tenant/file2.pdf",
            size=67890,
            last_modified="2024-01-02T00:00:00"
        )
    ],
    total=2
)
```

## Usage Examples

### Using Temporal Client

```python
from temporalio.client import Client
from gdai.temporal.upload_file import (
    UploadFileWorkflow,
    UploadFileInput,
)

# Connect to Temporal
client = await Client.connect("localhost:7233")

# Execute upload workflow
result = await client.execute_workflow(
    UploadFileWorkflow.run,
    UploadFileInput(
        tenant_id="customer-123",
        file_path="/tmp/document.pdf",
        object_name="important-doc.pdf",
    ),
    id=f"upload-workflow-{uuid4()}",
    task_queue="upload-file-queue",
)

if result.success:
    print(f"File uploaded to: {result.s3_url}")
else:
    print(f"Upload failed: {result.error_message}")
```

### Direct Activity Usage

```python
from gdai.temporal.upload_file.activity import upload_file
from gdai.temporal.upload_file import UploadFileInput

# Call activity directly (useful for testing)
result = await upload_file(
    UploadFileInput(
        tenant_id="customer-123",
        file_path="/tmp/document.pdf",
    )
)
```

## Multi-Tenant Isolation

All files are automatically organized by tenant ID:

```
s3://gdai-documents/
├── tenant-1/
│   ├── file1.pdf
│   └── file2.txt
├── tenant-2/
│   ├── file1.pdf
│   └── subdir/
│       └── file3.doc
└── tenant-3/
    └── file1.pdf
```

This ensures complete data isolation between tenants.

## Error Handling

All workflows include automatic retry policies:

- **Maximum attempts**: 3
- **Initial interval**: 1 second
- **Maximum interval**: 10 seconds
- **Backoff coefficient**: 2.0

Activities return detailed error messages in the output:

```python
UploadFileOutput(
    s3_key="",
    s3_url="",
    file_size=0,
    success=False,
    error_message="File not found: /tmp/nonexistent.pdf"
)
```

## Configuration

The module uses settings from environment variables:

```bash
# S3/MinIO Configuration
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=gdai-documents
S3_REGION=us-east-1
S3_USE_SSL=false

# Temporal Configuration
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default
```

## Task Queue

All workflows use the queue: `upload-file-queue`

## Worker

Start the file upload worker:

```bash
# As part of all workers
task temporal-all

# Or individually
python -m gdai.temporal.upload_file.worker
```

## Testing

Run the integration tests:

```bash
# All upload workflow tests
pytest tests/integration/test_upload_file_workflow.py -v

# Specific test
pytest tests/integration/test_upload_file_workflow.py::test_upload_file_activity -v
```

## Architecture

```
┌─────────────────┐
│   Client Code   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Workflows     │  ← Orchestration layer
│  - UploadFile   │
│  - DeleteFile   │
│  - ListFiles    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Activities    │  ← Execution layer
│  - upload_file  │
│  - delete_file  │
│  - list_files   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  S3 Storage     │  ← Storage layer
│   Service       │
└─────────────────┘
```

## Related Modules

- `gdai.services.s3_storage` - S3 storage service
- `gdai.temporal.extract_document` - Document extraction workflow
- `gdai.temporal.document_management` - Document CRUD operations
