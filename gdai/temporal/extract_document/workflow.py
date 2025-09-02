from datetime import timedelta

from temporalio import workflow

from .schema import ChunkDocumentInput, DocumentExtracInput, StoreDocumentInput, TempFiles


@workflow.defn
class DocumentExtractionWorkflow:
    @workflow.run
    async def run(self, document_input: DocumentExtracInput) -> str:
        await workflow.execute_activity("validate", document_input, schedule_to_close_timeout=timedelta(seconds=10))
        extracted_document_path = await workflow.execute_activity("extract", document_input, schedule_to_close_timeout=timedelta(seconds=50))
        chunk_files = await workflow.execute_activity(
            "chunk_texts",
            ChunkDocumentInput(chunk_strategy=document_input.chunk_strategy, extracted_document_path=extracted_document_path),
            schedule_to_close_timeout=timedelta(seconds=50),
        )

        embedded_files = []
        for chunk_file in chunk_files:
            chunk_with_embedding_file_path = await workflow.execute_child_workflow(
                "ChunkEmbeddingWorkflow", chunk_file, task_queue="embedding-chunks-queue", id=f"chunk-embedding-{chunk_file}"
            )

            await workflow.execute_activity(
                "store_embedded_chunks",
                StoreDocumentInput(
                    tenant_id=document_input.tenant_id,
                    document_original_path=document_input.document_path,
                    chunk_strategy=document_input.chunk_strategy,
                    document_chunks_path=chunk_with_embedding_file_path,
                ),
                schedule_to_close_timeout=timedelta(seconds=60),
            )
            embedded_files.append(chunk_with_embedding_file_path)

        await workflow.execute_activity(
            "remove_temp_files",
            TempFiles(extracted_document_file_path=extracted_document_path, chunk_files=chunk_files, embedded_files=embedded_files),
            schedule_to_close_timeout=timedelta(seconds=30),
        )

        return f"Document {document_input.document_path} validated successfully.  Chunks created: {len(chunk_files)}"
