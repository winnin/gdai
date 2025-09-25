from datetime import timedelta

from temporalio import workflow

from gdai.commons.logger import logger

from .schema import ChunkDocumentInput, DocumentExtracInput, StoreDocumentInput, TempFiles


@workflow.defn
class DocumentExtractionWorkflow:
    @workflow.run
    async def run(self, document_input: DocumentExtracInput) -> str:
        try:
            logger.info(
                f"Starting document extraction workflow for: {document_input.document_path} "
                f"(tenant: {document_input.tenant_id})"
            )
            logger.debug(f"Chunk strategy: {document_input.chunk_strategy}")

            # Validate document
            try:
                await workflow.execute_activity(
                    "validate", document_input, schedule_to_close_timeout=timedelta(seconds=10)
                )
                logger.info(f"Document validation completed for: {document_input.document_path}")
            except Exception as e:
                logger.error(f"Document validation failed for {document_input.document_path}: {e}")
                raise

            # Extract document content
            try:
                extracted_document_path = await workflow.execute_activity(
                    "extract", document_input, schedule_to_close_timeout=timedelta(seconds=50)
                )
                logger.info(f"Document extraction completed. Output: {extracted_document_path}")
            except Exception as e:
                logger.error(f"Document extraction failed for {document_input.document_path}: {e}")
                raise

            # Chunk texts
            try:
                chunk_files = await workflow.execute_activity(
                    "chunk_texts",
                    ChunkDocumentInput(
                        chunk_strategy=document_input.chunk_strategy, extracted_document_path=extracted_document_path
                    ),
                    schedule_to_close_timeout=timedelta(seconds=50),
                )
                logger.info(f"Text chunking completed. Generated {len(chunk_files)} chunk files")
            except Exception as e:
                logger.error(f"Text chunking failed for {document_input.document_path}: {e}")
                raise

            # Process embeddings for each chunk file
            embedded_files = []
            try:
                logger.info(f"Starting embedding processing for {len(chunk_files)} chunk files")

                for i, chunk_file in enumerate(chunk_files):
                    logger.debug(f"Processing chunk file {i+1}/{len(chunk_files)}: {chunk_file}")

                    try:
                        chunk_with_embedding_file_path = await workflow.execute_child_workflow(
                            "ChunkEmbeddingWorkflow",
                            chunk_file,
                            task_queue="embedding-chunks-queue",
                            id=f"chunk-embedding-{chunk_file}",
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

                        logger.debug(f"Successfully processed chunk file {i+1}/{len(chunk_files)}")

                    except Exception as e:
                        logger.error(f"Failed to process chunk file {chunk_file}: {e}")
                        raise

                logger.info(f"All {len(chunk_files)} chunk files processed successfully")

            except Exception as e:
                logger.error(f"Exception during chunk processing: {e}")
                raise

            # Clean up temporary files
            try:
                logger.info("Starting cleanup of temporary files")
                await workflow.execute_activity(
                    "remove_temp_files",
                    TempFiles(
                        extracted_document_file_path=extracted_document_path,
                        chunk_files=chunk_files,
                        embedded_files=embedded_files,
                    ),
                    schedule_to_close_timeout=timedelta(seconds=30),
                )
                logger.info("Temporary files cleanup completed")
            except Exception as e:
                logger.error(f"Error during temporary files cleanup: {e}")
                # Don't raise here as the main processing is complete

            logger.info(f"Document extraction workflow completed successfully for: {document_input.document_path}")
            return (
                f"Document {document_input.document_path} processed successfully. "
                f"Generated {len(chunk_files)} chunk files with embeddings."
            )

        except Exception as e:
            logger.error(f"Document extraction workflow failed: {e}")
            raise
