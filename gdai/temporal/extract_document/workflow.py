from datetime import timedelta

from temporalio import workflow

from gdai.commons.logger import logger

from .schema import ChunkDocumentInput, DocumentExtracInput


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
                raise e

            # Extract document content
            try:
                extracted_document_path = await workflow.execute_activity(
                    "extract", document_input, schedule_to_close_timeout=timedelta(seconds=50)
                )
                logger.info(f"Document extraction completed. Output: {extracted_document_path}")
            except Exception as e:
                logger.error(f"Document extraction failed for {document_input.document_path}: {e}")
                raise e

            # store document on database
            # TODO: implement it and send document id to chunks

            # Chunk texts
            try:
                batched_chunk_file = await workflow.execute_activity(
                    "chunk_texts_in_batched_files",
                    ChunkDocumentInput(
                        chunk_strategy=document_input.chunk_strategy, extracted_document_path=extracted_document_path
                    ),
                    schedule_to_close_timeout=timedelta(seconds=50),
                )
                logger.info(f"Text chunking completed. Generated chunk files: {len(batched_chunk_file)}")
            except Exception as e:
                logger.error(f"Text chunking failed for {document_input.document_path}: {e}")
                raise e

            # load each chunk file and send to embedding
            try:
                for chunk_file in batched_chunk_file:
                    chunk_data = await workflow.execute_activity(
                        "get_chunks_content_to_embedding", chunk_file, schedule_to_close_timeout=timedelta(seconds=50)
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
                        chunk_data.append(chunk)

                    # store embedded chunks
                    # TODO: implement chunk storage on database

                logger.info(f"All {len(batched_chunk_file)} chunk files processed successfully")

            except Exception as e:
                logger.error(f"Exception during chunk processing: {e}")
                raise e

            # Clean up temporary files
            files_to_remove = [extracted_document_path] + batched_chunk_file
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

            logger.info(f"Document extraction workflow completed successfully for: {document_input.document_path}")
            return (
                f"Document {document_input.document_path} processed successfully. "
                # f"Generated {len(chunk_files)} chunk files with embeddings."
            )

        except Exception as e:
            logger.error(f"Document extraction workflow failed: {e}")
            raise e
