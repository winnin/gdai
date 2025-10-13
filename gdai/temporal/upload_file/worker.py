"""Worker for file upload workflows."""

import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from gdai.commons.logger import logger
from gdai.commons.settings import get_settings

from .activity import (
    check_file_exists,
    delete_file,
    list_files,
    upload_file,
    upload_fileobj,
)
from .workflow import (
    CheckFileExistsWorkflow,
    DeleteFileWorkflow,
    ListFilesWorkflow,
    UploadFileobjWorkflow,
    UploadFileWorkflow,
)


async def main():
    """Start the file upload worker."""
    try:
        settings = get_settings()
        logger.info("Initializing File Upload worker...")

        client = await Client.connect(settings.temporal.host)
        logger.info(f"Successfully connected to Temporal server at {settings.temporal.host}")

        worker = Worker(
            client,
            task_queue="upload-file-queue",
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
        logger.info("Worker File Upload started using queue upload-file-queue")
        logger.info("Starting worker execution...")
        await worker.run()
    except Exception as e:
        logger.error(f"Failed to start File Upload worker: {e}")
        logger.exception("Worker startup error details")
        raise


if __name__ == "__main__":
    logger.info("Starting File Upload worker application...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"Worker application failed: {e}")
        logger.exception("Application error details")
        raise
