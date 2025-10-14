from datetime import timedelta

from temporalio import workflow

from .schema import (
    ChunkSearchParam,
    FormatAnswerInput,
    PromptInput,
    QueryInput,
    SearchInput,
    SearchResult,
    UpdateQueryResultInput,
)


@workflow.defn
class DocumentSearchWorkflow:
    @workflow.run
    async def run(self, search_input: SearchInput) -> SearchResult:
        try:
            workflow.logger.info(
                f"Starting document search workflow for query: {search_input.query_id}, "
                f"tenant: {search_input.tenant_id}"
            )
            workflow.logger.debug(
                f"Search parameters - similarity threshold: {search_input.similarity_threshold}, "
                f"max chunks: {search_input.max_num_chunks}"
            )

            # register query
            await workflow.execute_activity(
                "register_query",
                QueryInput(query_id=search_input.query_id, tenant_id=search_input.tenant_id, query=search_input.query),
                schedule_to_close_timeout=timedelta(seconds=10),
            )
            workflow.logger.info(f"Query {search_input.query_id} registered successfully")

            # embedding query
            workflow.logger.info(f"Starting query embedding for query: {search_input.query_id}")
            embedded_query_result = await workflow.execute_child_workflow(
                "TextEmbeddingWorkflow",
                {search_input.query_id: search_input.query},
                task_queue="embedding-text-queue",
                id=f"embed-query-{search_input.query_id}",
            )
            embedded_query = embedded_query_result[search_input.query_id]
            workflow.logger.info(f"Query embedding completed for query: {search_input.query_id}")

            # get chunks
            workflow.logger.info(f"Starting chunk retrieval for query: {search_input.query_id}")
            chunks = await workflow.execute_activity(
                "get_chunks",
                ChunkSearchParam(
                    tenant_id=search_input.tenant_id,
                    query_embedding=embedded_query,
                    limit=search_input.max_num_chunks,
                    similarity_threshold=search_input.similarity_threshold,
                    document_ids=search_input.document_ids,
                ),
                schedule_to_close_timeout=timedelta(seconds=30),
                result_type=list,
            )
            workflow.logger.info(f"Retrieved {len(chunks)} chunks for query: {search_input.query_id}")

            # generate prompt
            workflow.logger.info(f"Generating prompt for query: {search_input.query_id}")
            prompt = await workflow.execute_activity(
                "generate_prompt_from_template",
                PromptInput(query=search_input.query, chunks=chunks),
                schedule_to_close_timeout=timedelta(seconds=30),
                result_type=str,
            )
            workflow.logger.debug(f"Prompt generated with length: {len(prompt)}")

            # ask llm to answer the query based on the chunks and query
            workflow.logger.info(f"Starting LLM processing for query: {search_input.query_id}")
            llm_answer = await workflow.execute_child_workflow(
                "LLMWorkflow",
                {"user_prompt": prompt, "system_prompt": ""},
                task_queue="llm-queue",
                id=f"chat-query-{search_input.query_id}",
            )
            workflow.logger.info(f"LLM processing completed for query: {search_input.query_id}")

            # save query result on database
            workflow.logger.info(f"Saving query result for query: {search_input.query_id}")
            await workflow.execute_activity(
                "save_query_result",
                UpdateQueryResultInput(
                    query_id=search_input.query_id,
                    tenant_id=search_input.tenant_id,
                    answer=llm_answer,
                    status="completed",
                    chunks=chunks,
                ),
                schedule_to_close_timeout=timedelta(seconds=10),
            )

            # PREPARE RESULT TO SEND
            workflow.logger.info(f"Formatting final result for query: {search_input.query_id}")
            result = await workflow.execute_activity(
                "format_answer",
                FormatAnswerInput(
                    tenant_id=search_input.tenant_id,
                    query_id=search_input.query_id,
                    chunk_strategy="sentence",  # TODO: make it dynamic from request
                    query=search_input.query,
                    max_num_chunks=search_input.max_num_chunks,
                    document_ids=search_input.document_ids,
                    answer=llm_answer,
                    chunks=chunks,
                    similarity_threshold=search_input.similarity_threshold,
                ),
                schedule_to_close_timeout=timedelta(seconds=10),
                result_type=SearchResult,
            )

            workflow.logger.info(f"Document search workflow completed successfully for query: {search_input.query_id}")
            return result

        except Exception as e:
            workflow.logger.error(f"Error in document search workflow for query {search_input.query_id}: {e}")
            raise e
