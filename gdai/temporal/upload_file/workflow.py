"""Workflows for file upload operations."""

from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

from gdai.commons.logger import logger

from .schema import (
    CheckFileExistsInput,
    CheckFileExistsOutput,
    DeleteFileInput,
    DeleteFileOutput,
    ListFilesInput,
    ListFilesOutput,
    UploadFileInput,
    UploadFileobjInput,
    UploadFileOutput,
)


@workflow.defn
class UploadFileWorkflow:
    """Workflow to upload a file to S3."""

    @workflow.run
    async def run(self, input: UploadFileInput) -> UploadFileOutput:
        """Execute the file upload workflow.

        Args:
            input: Input containing tenant_id, file_path, and optional object_name

        Returns:
            UploadFileOutput: Result of the upload operation
        """
        try:
            logger.info(f"Starting upload file workflow for tenant: {input.tenant_id}")

            result = await workflow.execute_activity(
                "upload_file",
                input,
                schedule_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(
                    maximum_attempts=3,
                    initial_interval=timedelta(seconds=1),
                    maximum_interval=timedelta(seconds=10),
                    backoff_coefficient=2.0,
                ),
            )

            if result.success:
                logger.info(f"Upload file workflow completed successfully for tenant: {input.tenant_id}")
            else:
                logger.error(f"Upload file workflow failed for tenant: {input.tenant_id} - {result.error_message}")

            return result

        except Exception as e:
            logger.error(f"Upload file workflow failed for tenant {input.tenant_id}: {e}")
            return UploadFileOutput(
                s3_key="",
                s3_url="",
                file_size=0,
                success=False,
                error_message=str(e),
            )


@workflow.defn
class UploadFileobjWorkflow:
    """Workflow to upload a file object (in-memory) to S3."""

    @workflow.run
    async def run(self, input: UploadFileobjInput) -> UploadFileOutput:
        """Execute the file object upload workflow.

        Args:
            input: Input containing tenant_id, file_content, and object_name

        Returns:
            UploadFileOutput: Result of the upload operation
        """
        try:
            logger.info(f"Starting upload fileobj workflow for tenant: {input.tenant_id}")

            result = await workflow.execute_activity(
                "upload_fileobj",
                input,
                schedule_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(
                    maximum_attempts=3,
                    initial_interval=timedelta(seconds=1),
                    maximum_interval=timedelta(seconds=10),
                    backoff_coefficient=2.0,
                ),
            )

            if result.success:
                logger.info(f"Upload fileobj workflow completed successfully for tenant: {input.tenant_id}")
            else:
                logger.error(f"Upload fileobj workflow failed for tenant: {input.tenant_id} - {result.error_message}")

            return result

        except Exception as e:
            logger.error(f"Upload fileobj workflow failed for tenant {input.tenant_id}: {e}")
            return UploadFileOutput(
                s3_key="",
                s3_url="",
                file_size=0,
                success=False,
                error_message=str(e),
            )


@workflow.defn
class DeleteFileWorkflow:
    """Workflow to delete a file from S3."""

    @workflow.run
    async def run(self, input: DeleteFileInput) -> DeleteFileOutput:
        """Execute the file deletion workflow.

        Args:
            input: Input containing s3_key

        Returns:
            DeleteFileOutput: Result of the deletion operation
        """
        try:
            logger.info(f"Starting delete file workflow for file: {input.s3_key}")

            result = await workflow.execute_activity(
                "delete_file",
                input,
                schedule_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(
                    maximum_attempts=3,
                    initial_interval=timedelta(seconds=1),
                    maximum_interval=timedelta(seconds=10),
                    backoff_coefficient=2.0,
                ),
            )

            if result.success:
                logger.info(f"Delete file workflow completed successfully for file: {input.s3_key}")
            else:
                logger.error(f"Delete file workflow failed for file: {input.s3_key} - {result.error_message}")

            return result

        except Exception as e:
            logger.error(f"Delete file workflow failed for file {input.s3_key}: {e}")
            return DeleteFileOutput(
                s3_key=input.s3_key,
                success=False,
                error_message=str(e),
            )


@workflow.defn
class CheckFileExistsWorkflow:
    """Workflow to check if a file exists in S3."""

    @workflow.run
    async def run(self, input: CheckFileExistsInput) -> CheckFileExistsOutput:
        """Execute the file existence check workflow.

        Args:
            input: Input containing s3_key

        Returns:
            CheckFileExistsOutput: Result of the existence check
        """
        try:
            logger.info(f"Starting check file exists workflow for file: {input.s3_key}")

            result = await workflow.execute_activity(
                "check_file_exists",
                input,
                schedule_to_close_timeout=timedelta(seconds=30),
            )

            logger.info(f"Check file exists workflow completed for file: {input.s3_key}")
            return result

        except Exception as e:
            logger.error(f"Check file exists workflow failed for file {input.s3_key}: {e}")
            raise


@workflow.defn
class ListFilesWorkflow:
    """Workflow to list files in S3 for a tenant."""

    @workflow.run
    async def run(self, input: ListFilesInput) -> ListFilesOutput:
        """Execute the list files workflow.

        Args:
            input: Input containing tenant_id and optional prefix

        Returns:
            ListFilesOutput: List of files and total count
        """
        try:
            logger.info(f"Starting list files workflow for tenant: {input.tenant_id}")

            result = await workflow.execute_activity(
                "list_files",
                input,
                schedule_to_close_timeout=timedelta(minutes=2),
            )

            logger.info(f"List files workflow completed for tenant: {input.tenant_id}")
            return result

        except Exception as e:
            logger.error(f"List files workflow failed for tenant {input.tenant_id}: {e}")
            raise
