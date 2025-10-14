from datetime import timedelta

from temporalio import workflow

from gdai.commons.logger import logger

from .schema import Chunk, ChunkDocumentInput, DocumentExtracInput


@workflow.defn
class DocumentExtractionWorkflow:
    async def _validate_document(self, document_input: DocumentExtracInput) -> None:
        """Validate document input and file existence"""
        try:
            await workflow.execute_activity("validate", document_input, schedule_to_close_timeout=timedelta(seconds=10))
            logger.info(f"Document validation completed for: {document_input.s3_key}")
        except Exception as e:
            logger.error(f"Document validation failed for {document_input.s3_key}: {e}")
            raise e

    async def _save_document_metadata(self, document_input: DocumentExtracInput) -> str:
        """Save document metadata to database"""
        try:
            document_id = await workflow.execute_activity(
                "save_document_metadata", document_input, schedule_to_close_timeout=timedelta(seconds=20)
            )
            logger.info(f"Document metadata saved with ID: {document_id}")
            return document_id
        except Exception as e:
            logger.error(f"Saving document metadata failed for {document_input.s3_key}: {e}")
            raise e

    async def _extract_document_content(self, document_input: DocumentExtracInput) -> str:
        """Extract content from document"""
        try:
            extracted_document_path = await workflow.execute_activity(
                "extract_document_content", document_input, schedule_to_close_timeout=timedelta(seconds=50)
            )
            logger.info(f"Document extraction completed. Output: {extracted_document_path}")
            return extracted_document_path
        except Exception as e:
            logger.error(f"Document extraction failed for {document_input.s3_key}: {e}")
            raise e

    async def _chunk_texts_to_batched_files(
        self, document_id: str, document_input: DocumentExtracInput, extracted_document_path: str
    ) -> list[str]:
        """Chunk document texts into batched files"""
        try:
            batched_chunk_file = await workflow.execute_activity(
                "chunk_texts_to_batched_files",
                ChunkDocumentInput(
                    document_id=document_id,
                    tenant_id=document_input.tenant_id,
                    chunk_strategy=document_input.chunk_strategy,
                    extracted_document_path=extracted_document_path,
                ),
                schedule_to_close_timeout=timedelta(seconds=50),
            )
            logger.info(f"Text chunking completed. Generated chunk files: {len(batched_chunk_file)}")
            return batched_chunk_file
        except Exception as e:
            logger.error(f"Text chunking failed for {document_input.s3_key}: {e}")
            raise e

    async def _get_chunk_file_content_for_embedding(self, batched_chunk_file: str) -> list[Chunk]:
        """Process chunks for embedding"""
        try:
            chunk_data = await workflow.execute_activity(
                "get_chunk_file_content_for_embedding",
                batched_chunk_file,
                schedule_to_close_timeout=timedelta(seconds=50),
            )
            content_to_embedding = {chunk["id"]: chunk["chunk"] for chunk in chunk_data}
            embeddings = await workflow.execute_child_workflow(
                "TextEmbeddingWorkflow",
                content_to_embedding,
                task_queue="embedding-text-queue",
            )

            # update chunks with embeddings
            for chunk in chunk_data:
                chunk["embedding"] = embeddings.get(chunk["id"])

            logger.info(f"All {len(batched_chunk_file)} chunk files processed successfully")
            return chunk_data

        except Exception as e:
            logger.error(f"Exception during chunk processing: {e}")
            raise e

    async def _store_embedded_chunks(self, chunks: list[Chunk]) -> None:
        """Store embedded chunks into database"""
        try:
            await workflow.execute_activity(
                "store_embedded_chunks",
                chunks,
                schedule_to_close_timeout=timedelta(seconds=50),
            )
            logger.info(f"Stored {len(chunks)} embedded chunks into database successfully")
        except Exception as e:
            logger.error(f"Error storing embedded chunks into database: {e}")
            raise e

    async def _cleanup_temp_files(self, files_to_remove: list[str]) -> None:
        """Clean up temporary files"""
        try:
            logger.info("Starting cleanup of temporary files")
            await workflow.execute_activity(
                "remove_temp_files",
                files_to_remove,
                schedule_to_close_timeout=timedelta(seconds=30),
            )
            logger.info("Temporary files cleanup completed")
        except Exception as e:
            logger.error(f"Error during temporary files cleanup: {e}")
            # Don't raise here as the main processing is complete

    @workflow.run
    async def run(self, document_input: DocumentExtracInput) -> str:
        extracted_document_path = ""
        batched_chunk_files = []
        document_id = ""
        try:
            logger.info(
                f"Starting document extraction workflow for: {document_input.s3_key} "
                f"(tenant: {document_input.tenant_id})"
                f" with chunk strategy: {document_input.chunk_strategy}"
            )

            # Validate document
            await self._validate_document(document_input)

            # store document metadata into database
            document_id = await self._save_document_metadata(document_input)

            # Extract document content
            extracted_document_path = await self._extract_document_content(document_input)

            # Chunk texts into multiple files (each file has a limited number of chunks)
            batched_chunk_files = await self._chunk_texts_to_batched_files(
                document_id, document_input, extracted_document_path
            )

            # load each chunk file and get the embedding for each chunk using TextEmbeddingWorkflow
            for file_path in batched_chunk_files:
                chunks_with_embeddings = await self._get_chunk_file_content_for_embedding(file_path)
                # Store document chunks metadata into database
                await self._store_embedded_chunks(chunks_with_embeddings)
                logger.info(f"Stored chunks from file {file_path} into database successfully")

            logger.info(f"Document extraction workflow completed successfully for: {document_input.s3_key}")
            return document_id

        except Exception as e:
            logger.error(f"Document extraction workflow failed: {e}")
            raise e

        finally:
            logger.info("Document extraction workflow finished.")
            files_to_remove = [extracted_document_path] + batched_chunk_files
            await self._cleanup_temp_files(files_to_remove)
