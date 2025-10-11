"""Workflows for document management operations."""

from datetime import timedelta

from temporalio import workflow

from gdai.commons.logger import logger

from .schema import (
    DeleteDocumentInput,
    Document,
    DocumentStatus,
    GetDocumentChunksInput,
    GetDocumentChunksOutput,
    GetDocumentInput,
    GetDocumentStatusInput,
    ListDocumentsInput,
    ListDocumentsOutput,
)


@workflow.defn
class ListDocumentsWorkflow:
    """Workflow to list all documents for a tenant."""

    @workflow.run
    async def run(self, input: ListDocumentsInput) -> ListDocumentsOutput:
        """Execute the list documents workflow.

        Args:
            input: Input containing tenant_id

        Returns:
            ListDocumentsOutput: List of documents and total count
        """
        try:
            logger.info(f"Starting list documents workflow for tenant: {input.tenant_id}")

            result = await workflow.execute_activity(
                "list_documents",
                input,
                schedule_to_close_timeout=timedelta(seconds=30),
            )

            logger.info(f"List documents workflow completed for tenant: {input.tenant_id}")
            return result

        except Exception as e:
            logger.error(f"List documents workflow failed for tenant {input.tenant_id}: {e}")
            raise e


@workflow.defn
class GetDocumentWorkflow:
    """Workflow to get a specific document by ID."""

    @workflow.run
    async def run(self, input: GetDocumentInput) -> Document:
        """Execute the get document workflow.

        Args:
            input: Input containing tenant_id and document_id

        Returns:
            Document: The requested document
        """
        try:
            logger.info(f"Starting get document workflow for document: {input.document_id}")

            result = await workflow.execute_activity(
                "get_document",
                input,
                schedule_to_close_timeout=timedelta(seconds=30),
            )

            logger.info(f"Get document workflow completed for document: {input.document_id}")
            return result

        except Exception as e:
            logger.error(f"Get document workflow failed for document {input.document_id}: {e}")
            raise e


@workflow.defn
class DeleteDocumentWorkflow:
    """Workflow to delete a document and all its associated chunks."""

    @workflow.run
    async def run(self, input: DeleteDocumentInput) -> bool:
        """Execute the delete document workflow.

        Args:
            input: Input containing tenant_id and document_id

        Returns:
            bool: True if deletion was successful
        """
        try:
            logger.info(f"Starting delete document workflow for document: {input.document_id}")

            result = await workflow.execute_activity(
                "delete_document",
                input,
                schedule_to_close_timeout=timedelta(seconds=30),
            )

            logger.info(f"Delete document workflow completed for document: {input.document_id}")
            return result

        except Exception as e:
            logger.error(f"Delete document workflow failed for document {input.document_id}: {e}")
            raise e


@workflow.defn
class GetDocumentChunksWorkflow:
    """Workflow to get all chunks for a specific document."""

    @workflow.run
    async def run(self, input: GetDocumentChunksInput) -> GetDocumentChunksOutput:
        """Execute the get document chunks workflow.

        Args:
            input: Input containing tenant_id and document_id

        Returns:
            GetDocumentChunksOutput: List of chunks and total count
        """
        try:
            logger.info(f"Starting get document chunks workflow for document: {input.document_id}")

            result = await workflow.execute_activity(
                "get_document_chunks",
                input,
                schedule_to_close_timeout=timedelta(seconds=30),
            )

            logger.info(f"Get document chunks workflow completed for document: {input.document_id}")
            return result

        except Exception as e:
            logger.error(f"Get document chunks workflow failed for document {input.document_id}: {e}")
            raise e


@workflow.defn
class GetDocumentStatusWorkflow:
    """Workflow to get the processing status of a document."""

    @workflow.run
    async def run(self, input: GetDocumentStatusInput) -> DocumentStatus:
        """Execute the get document status workflow.

        Args:
            input: Input containing tenant_id and document_id

        Returns:
            DocumentStatus: Document status information
        """
        try:
            logger.info(f"Starting get document status workflow for document: {input.document_id}")

            result = await workflow.execute_activity(
                "get_document_status",
                input,
                schedule_to_close_timeout=timedelta(seconds=30),
            )

            logger.info(f"Get document status workflow completed for document: {input.document_id}")
            return result

        except Exception as e:
            logger.error(f"Get document status workflow failed for document {input.document_id}: {e}")
            raise e
