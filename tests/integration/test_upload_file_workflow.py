"""Integration tests for file upload workflows."""

import asyncio
import io
import tempfile
from pathlib import Path
from uuid import uuid4

import pytest
import pytest_asyncio
from temporalio.client import Client
from temporalio.worker import Worker

from gdai.commons.settings import get_settings
from gdai.services.s3_storage import get_s3_storage
from gdai.temporal.upload_file import (
    CheckFileExistsInput,
    DeleteFileInput,
    ListFilesInput,
    UploadFileInput,
    UploadFileobjInput,
)
from gdai.temporal.upload_file.activity import (
    check_file_exists,
    delete_file,
    list_files,
    upload_file,
    upload_fileobj,
)
from gdai.temporal.upload_file.workflow import (
    CheckFileExistsWorkflow,
    DeleteFileWorkflow,
    ListFilesWorkflow,
    UploadFileobjWorkflow,
    UploadFileWorkflow,
)


@pytest.fixture
def tenant_id() -> str:
    """Generate a unique tenant ID for testing."""
    return f"test-tenant-{uuid4()}"


@pytest.fixture
def temp_file() -> Path:
    """Create a temporary file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write("Test file content for upload workflow testing\n")
        f.write("This is line 2\n")
        f.write("This is line 3\n")
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest_asyncio.fixture
async def temporal_client():
    """Get a Temporal client for testing."""
    settings = get_settings()
    client = await Client.connect(settings.temporal.host)
    return client


@pytest_asyncio.fixture
async def upload_worker(temporal_client):
    """Start a Temporal worker for upload workflows."""
    worker = Worker(
        temporal_client,
        task_queue="upload-file-queue-test",
        workflows=[
            UploadFileWorkflow,
            UploadFileobjWorkflow,
            DeleteFileWorkflow,
            CheckFileExistsWorkflow,
            ListFilesWorkflow,
        ],
        activities=[
            upload_file,
            upload_fileobj,
            delete_file,
            check_file_exists,
            list_files,
        ],
    )

    # Run worker in background
    worker_task = asyncio.create_task(worker.run())

    yield worker

    # Stop worker
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass


@pytest.mark.asyncio
async def test_upload_file_activity(temp_file: Path, tenant_id: str):
    """Test upload_file activity."""
    input_data = UploadFileInput(
        tenant_id=tenant_id,
        file_path=str(temp_file),
        object_name="test-upload.txt",
    )

    result = await upload_file(input_data)

    assert result.success is True
    assert result.error_message is None
    assert result.s3_key == f"{tenant_id}/test-upload.txt"
    assert result.file_size > 0
    assert result.s3_url.startswith("s3://")

    # Cleanup
    s3_storage = get_s3_storage()
    s3_storage.delete_file(result.s3_key)


@pytest.mark.asyncio
async def test_upload_file_activity_file_not_found(tenant_id: str):
    """Test upload_file activity with non-existent file."""
    input_data = UploadFileInput(
        tenant_id=tenant_id,
        file_path="/tmp/nonexistent-file-12345.txt",
        object_name="test-upload.txt",
    )

    result = await upload_file(input_data)

    assert result.success is False
    assert result.error_message is not None
    assert "File not found" in result.error_message
    assert result.s3_key == ""


@pytest.mark.asyncio
async def test_upload_fileobj_activity(tenant_id: str):
    """Test upload_fileobj activity."""
    file_content = b"Test content for fileobj upload"

    input_data = UploadFileobjInput(
        tenant_id=tenant_id,
        file_content=file_content,
        object_name="test-fileobj.txt",
    )

    result = await upload_fileobj(input_data)

    assert result.success is True
    assert result.error_message is None
    assert result.s3_key == f"{tenant_id}/test-fileobj.txt"
    assert result.file_size == len(file_content)

    # Cleanup
    s3_storage = get_s3_storage()
    s3_storage.delete_file(result.s3_key)


@pytest.mark.asyncio
async def test_delete_file_activity(tenant_id: str):
    """Test delete_file activity."""
    # First upload a file
    s3_storage = get_s3_storage()
    file_obj = io.BytesIO(b"Test content")
    s3_key = s3_storage.upload_fileobj(tenant_id, file_obj, "test-delete.txt")

    # Now delete it
    input_data = DeleteFileInput(s3_key=s3_key)
    result = await delete_file(input_data)

    assert result.success is True
    assert result.error_message is None
    assert result.s3_key == s3_key

    # Verify file is deleted
    assert not s3_storage.file_exists(s3_key)


@pytest.mark.asyncio
async def test_check_file_exists_activity(tenant_id: str):
    """Test check_file_exists activity."""
    # Upload a test file
    s3_storage = get_s3_storage()
    file_obj = io.BytesIO(b"Test content")
    s3_key = s3_storage.upload_fileobj(tenant_id, file_obj, "test-exists.txt")

    try:
        # Check that file exists
        input_data = CheckFileExistsInput(s3_key=s3_key)
        result = await check_file_exists(input_data)

        assert result.exists is True
        assert result.s3_key == s3_key

        # Check non-existent file
        input_data = CheckFileExistsInput(s3_key=f"{tenant_id}/nonexistent.txt")
        result = await check_file_exists(input_data)

        assert result.exists is False

    finally:
        # Cleanup
        s3_storage.delete_file(s3_key)


@pytest.mark.asyncio
async def test_list_files_activity(tenant_id: str):
    """Test list_files activity."""
    s3_storage = get_s3_storage()

    # Upload multiple test files
    file1 = io.BytesIO(b"Content 1")
    file2 = io.BytesIO(b"Content 2")
    file3 = io.BytesIO(b"Content 3")

    s3_key1 = s3_storage.upload_fileobj(tenant_id, file1, "file1.txt")
    s3_key2 = s3_storage.upload_fileobj(tenant_id, file2, "file2.txt")
    s3_key3 = s3_storage.upload_fileobj(tenant_id, file3, "subdir/file3.txt")

    try:
        # List all files for tenant
        input_data = ListFilesInput(tenant_id=tenant_id)
        result = await list_files(input_data)

        assert result.total == 3
        assert len(result.files) == 3
        assert all(f.s3_key.startswith(tenant_id) for f in result.files)

        # List files with prefix
        input_data = ListFilesInput(tenant_id=tenant_id, prefix="subdir")
        result = await list_files(input_data)

        assert result.total == 1
        assert result.files[0].s3_key == s3_key3

    finally:
        # Cleanup
        s3_storage.delete_file(s3_key1)
        s3_storage.delete_file(s3_key2)
        s3_storage.delete_file(s3_key3)


@pytest.mark.skip(reason="Requires Temporal server running")
@pytest.mark.asyncio
async def test_upload_file_workflow(temporal_client, upload_worker, temp_file: Path, tenant_id: str):
    """Test UploadFileWorkflow end-to-end."""
    input_data = UploadFileInput(
        tenant_id=tenant_id,
        file_path=str(temp_file),
        object_name="workflow-test.txt",
    )

    result = await temporal_client.execute_workflow(
        UploadFileWorkflow.run,
        input_data,
        id=f"upload-file-workflow-{uuid4()}",
        task_queue="upload-file-queue-test",
    )

    assert result.success is True
    assert result.s3_key == f"{tenant_id}/workflow-test.txt"
    assert result.file_size > 0

    # Verify file exists in S3
    s3_storage = get_s3_storage()
    assert s3_storage.file_exists(result.s3_key)

    # Cleanup
    s3_storage.delete_file(result.s3_key)


@pytest.mark.skip(reason="Requires Temporal server running")
@pytest.mark.asyncio
async def test_upload_fileobj_workflow(temporal_client, upload_worker, tenant_id: str):
    """Test UploadFileobjWorkflow end-to-end."""
    file_content = b"Workflow test content"

    input_data = UploadFileobjInput(
        tenant_id=tenant_id,
        file_content=file_content,
        object_name="workflow-fileobj-test.txt",
    )

    result = await temporal_client.execute_workflow(
        UploadFileobjWorkflow.run,
        input_data,
        id=f"upload-fileobj-workflow-{uuid4()}",
        task_queue="upload-file-queue-test",
    )

    assert result.success is True
    assert result.s3_key == f"{tenant_id}/workflow-fileobj-test.txt"
    assert result.file_size == len(file_content)

    # Verify file exists in S3
    s3_storage = get_s3_storage()
    assert s3_storage.file_exists(result.s3_key)

    # Cleanup
    s3_storage.delete_file(result.s3_key)


@pytest.mark.skip(reason="Requires Temporal server running")
@pytest.mark.asyncio
async def test_delete_file_workflow(temporal_client, upload_worker, tenant_id: str):
    """Test DeleteFileWorkflow end-to-end."""
    # First upload a file
    s3_storage = get_s3_storage()
    file_obj = io.BytesIO(b"Test content for deletion")
    s3_key = s3_storage.upload_fileobj(tenant_id, file_obj, "workflow-delete-test.txt")

    # Execute delete workflow
    input_data = DeleteFileInput(s3_key=s3_key)

    result = await temporal_client.execute_workflow(
        DeleteFileWorkflow.run,
        input_data,
        id=f"delete-file-workflow-{uuid4()}",
        task_queue="upload-file-queue-test",
    )

    assert result.success is True
    assert result.s3_key == s3_key

    # Verify file is deleted
    assert not s3_storage.file_exists(s3_key)


@pytest.mark.skip(reason="Requires Temporal server running")
@pytest.mark.asyncio
async def test_check_file_exists_workflow(temporal_client, upload_worker, tenant_id: str):
    """Test CheckFileExistsWorkflow end-to-end."""
    # Upload a test file
    s3_storage = get_s3_storage()
    file_obj = io.BytesIO(b"Test content")
    s3_key = s3_storage.upload_fileobj(tenant_id, file_obj, "workflow-exists-test.txt")

    try:
        # Check that file exists
        input_data = CheckFileExistsInput(s3_key=s3_key)

        result = await temporal_client.execute_workflow(
            CheckFileExistsWorkflow.run,
            input_data,
            id=f"check-exists-workflow-{uuid4()}",
            task_queue="upload-file-queue-test",
        )

        assert result.exists is True
        assert result.s3_key == s3_key

    finally:
        # Cleanup
        s3_storage.delete_file(s3_key)


@pytest.mark.skip(reason="Requires Temporal server running")
@pytest.mark.asyncio
async def test_list_files_workflow(temporal_client, upload_worker, tenant_id: str):
    """Test ListFilesWorkflow end-to-end."""
    s3_storage = get_s3_storage()

    # Upload test files
    file1 = io.BytesIO(b"Content 1")
    file2 = io.BytesIO(b"Content 2")

    s3_key1 = s3_storage.upload_fileobj(tenant_id, file1, "workflow-list-1.txt")
    s3_key2 = s3_storage.upload_fileobj(tenant_id, file2, "workflow-list-2.txt")

    try:
        # Execute list workflow
        input_data = ListFilesInput(tenant_id=tenant_id)

        result = await temporal_client.execute_workflow(
            ListFilesWorkflow.run,
            input_data,
            id=f"list-files-workflow-{uuid4()}",
            task_queue="upload-file-queue-test",
        )

        assert result.total >= 2
        assert len(result.files) >= 2
        assert any(f.s3_key == s3_key1 for f in result.files)
        assert any(f.s3_key == s3_key2 for f in result.files)

    finally:
        # Cleanup
        s3_storage.delete_file(s3_key1)
        s3_storage.delete_file(s3_key2)
