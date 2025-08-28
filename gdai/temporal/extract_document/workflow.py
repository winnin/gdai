from datetime import timedelta

from temporalio import workflow

from .schema import ChunkDocumentInput, DocumentExtracInput, StoreDocumentInput


@workflow.defn
class DocumentExtractionWorkflow:
    @workflow.run
    async def run(self, document_input: DocumentExtracInput) -> str:
        await workflow.execute_activity("validate", document_input, schedule_to_close_timeout=timedelta(seconds=10))
        extracted_document_path = await workflow.execute_activity("extract", document_input, schedule_to_close_timeout=timedelta(seconds=50))
        chunk_file_path = await workflow.execute_activity(
            "chunk_texts",
            ChunkDocumentInput(chunk_strategy=document_input.chunk_strategy, extracted_document_path=extracted_document_path),
            schedule_to_close_timeout=timedelta(seconds=50),
        )
        await workflow.execute_activity(
            "store",
            StoreDocumentInput(
                tenant_id=document_input.tenant_id,
                chunk_strategy=document_input.chunk_strategy,
                document_original_path=document_input.document_path,
                document_chunks_path=chunk_file_path,
            ),
            schedule_to_close_timeout=timedelta(seconds=30),
        )
        return f"Document {document_input.document_path} validated successfully. {chunk_file_path}"
