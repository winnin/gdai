from datetime import timedelta

from temporalio import workflow

from .schema import PromptInput, QueryInput, SearchInput, SearchQueryParam, SearchResult


@workflow.defn
class DocumentSearchWorkflow:
    @workflow.run
    async def run(self, search_input: SearchInput) -> SearchResult:
        try:
            # register query
            await workflow.execute_activity(
                "register_query",
                QueryInput(query_id=search_input.query_id, tenant_id=search_input.tenant_id, query=search_input.query),
                schedule_to_close_timeout=timedelta(seconds=10),
            )

            # embedding query
            embedded_query_result = await workflow.execute_child_workflow(
                "TextEmbeddingWorkflow",
                {search_input.query_id: search_input.query},
                task_queue="embedding-text-queue",
                id=f"embed-query-{search_input.query_id}",
            )
            embedded_query = embedded_query_result[search_input.query_id]

            # get chunks
            chunks = await workflow.execute_activity(
                "get_chunks",
                SearchQueryParam(
                    tenant_id=search_input.tenant_id,
                    query_embedding=embedded_query,
                    limit=search_input.max_num_chunks,
                    similarity_threshold=search_input.similarity_threshold,
                    document_ids=search_input.document_ids,
                ),
                schedule_to_close_timeout=timedelta(seconds=30),
            )

            # generate prompt
            prompt = await workflow.execute_activity(
                "generate_prompt_from_template",
                PromptInput(query=search_input.query, chunks=chunks),
                schedule_to_close_timeout=timedelta(seconds=30),
            )

            # ask llm to answer the query based on the chunks and query
            llm_answer = await workflow.execute_child_workflow(
                "LLMWorkflow",
                {"user_prompt": prompt, "system_prompt": ""},
                task_queue="llm-queue",
                id=f"chat-query-{search_input.query_id}",
            )

            # save query result on database
            # TODO

            # PREPARE RESULT TO SEND
            return llm_answer

        except Exception as e:
            print(e)
            raise e

        # result = SearchResult(
        #     query_id=search_input.query_id,
        #     query=search_input.query,
        #     answer=llm_answer,
        #     tenant_id=search_input.tenant_id,
        #     chunks=chunks,
        # )

        # return result
        return None
