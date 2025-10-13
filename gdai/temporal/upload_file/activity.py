"""Activities for file upload workflows."""

import io
from pathlib import Path

from temporalio import activity

from gdai.commons.logger import logger
from gdai.services.s3_storage import get_s3_storage

from .schema import (
    CheckFileExistsInput,
    CheckFileExistsOutput,
    DeleteFileInput,
    DeleteFileOutput,
    FileInfo,
    ListFilesInput,
    ListFilesOutput,
    UploadFileInput,
    UploadFileobjInput,
    UploadFileOutput,
)


@activity.defn
async def upload_file(input: UploadFileInput) -> UploadFileOutput:
    """Upload a file to S3 with tenant isolation.

    Args:
        input: Input containing tenant_id, file_path, and optional object_name

    Returns:
        UploadFileOutput: Result of the upload operation

    Raises:
        FileNotFoundError: If the file doesn't exist
        Exception: If upload fails
    """
    try:
        logger.info(f"Uploading file {input.file_path} for tenant {input.tenant_id}")

        # Check if file exists
        file_path = Path(input.file_path)
        if not file_path.exists():
            error_msg = f"File not found: {input.file_path}"
            logger.error(error_msg)
            return UploadFileOutput(
                s3_key="",
                s3_url="",
                file_size=0,
                success=False,
                error_message=error_msg,
            )

        # Get file size
        file_size = file_path.stat().st_size

        # Upload to S3
        s3_storage = get_s3_storage()
        s3_key = s3_storage.upload_file(
            tenant_id=input.tenant_id,
            file_path=input.file_path,
            object_name=input.object_name,
        )
        s3_url = s3_storage.get_file_url(s3_key)

        logger.info(f"Successfully uploaded file to {s3_url}")
        return UploadFileOutput(
            s3_key=s3_key,
            s3_url=s3_url,
            file_size=file_size,
            success=True,
        )

    except FileNotFoundError:
        error_msg = f"File not found: {input.file_path}"
        logger.error(error_msg)
        return UploadFileOutput(
            s3_key="",
            s3_url="",
            file_size=0,
            success=False,
            error_message=error_msg,
        )
    except Exception as e:
        error_msg = f"Failed to upload file: {str(e)}"
        logger.error(error_msg)
        logger.exception("Upload error details")
        return UploadFileOutput(
            s3_key="",
            s3_url="",
            file_size=0,
            success=False,
            error_message=error_msg,
        )


@activity.defn
async def upload_fileobj(input: UploadFileobjInput) -> UploadFileOutput:
    """Upload a file object (in-memory) to S3 with tenant isolation.

    Args:
        input: Input containing tenant_id, file_content, and object_name

    Returns:
        UploadFileOutput: Result of the upload operation

    Raises:
        Exception: If upload fails
    """
    try:
        logger.info(f"Uploading file object {input.object_name} for tenant {input.tenant_id}")

        # Get file size
        file_size = len(input.file_content)

        # Create file-like object from bytes
        file_obj = io.BytesIO(input.file_content)

        # Upload to S3
        s3_storage = get_s3_storage()
        s3_key = s3_storage.upload_fileobj(
            tenant_id=input.tenant_id,
            file_obj=file_obj,
            object_name=input.object_name,
        )
        s3_url = s3_storage.get_file_url(s3_key)

        logger.info(f"Successfully uploaded file object to {s3_url}")
        return UploadFileOutput(
            s3_key=s3_key,
            s3_url=s3_url,
            file_size=file_size,
            success=True,
        )

    except Exception as e:
        error_msg = f"Failed to upload file object: {str(e)}"
        logger.error(error_msg)
        logger.exception("Upload error details")
        return UploadFileOutput(
            s3_key="",
            s3_url="",
            file_size=0,
            success=False,
            error_message=error_msg,
        )


@activity.defn
async def delete_file(input: DeleteFileInput) -> DeleteFileOutput:
    """Delete a file from S3.

    Args:
        input: Input containing s3_key

    Returns:
        DeleteFileOutput: Result of the deletion operation

    Raises:
        Exception: If deletion fails
    """
    try:
        logger.info(f"Deleting file {input.s3_key} from S3")

        s3_storage = get_s3_storage()
        s3_storage.delete_file(input.s3_key)

        logger.info(f"Successfully deleted file {input.s3_key}")
        return DeleteFileOutput(
            s3_key=input.s3_key,
            success=True,
        )

    except Exception as e:
        error_msg = f"Failed to delete file: {str(e)}"
        logger.error(error_msg)
        logger.exception("Deletion error details")
        return DeleteFileOutput(
            s3_key=input.s3_key,
            success=False,
            error_message=error_msg,
        )


@activity.defn
async def check_file_exists(input: CheckFileExistsInput) -> CheckFileExistsOutput:
    """Check if a file exists in S3.

    Args:
        input: Input containing s3_key

    Returns:
        CheckFileExistsOutput: Result of the existence check

    Raises:
        Exception: If check fails
    """
    try:
        logger.info(f"Checking if file {input.s3_key} exists in S3")

        s3_storage = get_s3_storage()
        exists = s3_storage.file_exists(input.s3_key)

        logger.info(f"File {input.s3_key} exists: {exists}")
        return CheckFileExistsOutput(
            s3_key=input.s3_key,
            exists=exists,
        )

    except Exception as e:
        logger.error(f"Failed to check file existence: {e}")
        logger.exception("Existence check error details")
        raise


@activity.defn
async def list_files(input: ListFilesInput) -> ListFilesOutput:
    """List all files for a tenant in S3.

    Args:
        input: Input containing tenant_id and optional prefix

    Returns:
        ListFilesOutput: List of files and total count

    Raises:
        Exception: If listing fails
    """
    try:
        logger.info(f"Listing files for tenant {input.tenant_id} with prefix '{input.prefix}'")

        s3_storage = get_s3_storage()
        s3_keys = s3_storage.list_files(input.tenant_id, input.prefix)

        # Get file info for each key
        files = []
        for s3_key in s3_keys:
            try:
                # Get object metadata
                response = s3_storage.client.head_object(
                    Bucket=s3_storage.bucket,
                    Key=s3_key,
                )
                files.append(
                    FileInfo(
                        s3_key=s3_key,
                        size=response["ContentLength"],
                        last_modified=response["LastModified"].isoformat(),
                    )
                )
            except Exception as e:
                logger.warning(f"Failed to get metadata for {s3_key}: {e}")

        logger.info(f"Found {len(files)} files for tenant {input.tenant_id}")
        return ListFilesOutput(
            files=files,
            total=len(files),
        )

    except Exception as e:
        logger.error(f"Failed to list files: {e}")
        logger.exception("List files error details")
        raise
