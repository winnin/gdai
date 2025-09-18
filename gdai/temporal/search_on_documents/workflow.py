from datetime import timedelta

from temporalio import workflow

from gdai.temporal.search_on_documents.schema import SearchInput, SearchResult


@workflow.defn
class DocumentSearchWorkflow:
    @workflow.run
    async def run(self, search_input: SearchInput) -> SearchResult:
        # embedding query
        embedded_query_result = await workflow.execute_child_workflow(
            "TextEmbeddingWorkflow",
            {search_input.query_id: search_input.query},
            task_queue="embedding-text-queue",
            id=f"embed-query-{search_input.query_id}",
        )
        embedded_query = embedded_query_result[search_input.query_id]

        # get all related chunks
        chunks = await workflow.execute_activity(
            "get_chunks",
            embedded_query,
            search_input.tenant_id,
            search_input.max_num_chunks,
            search_input.similarity_threshold,
            search_input.document_ids,
            schedule_to_close_timeout=timedelta(seconds=30),
        )

        # generate prompt
        prompt = await workflow.execute_activity(
            "generate_prompt_from_template",
            search_input.query,
            chunks,
            schedule_to_close_timeout=timedelta(seconds=30),
        )

        # ask llm to answer the query based on the chunks and query
        llm_answer = await workflow.execute_child_workflow(
            "LLMChatWorkflow",
            {"user_prompt": prompt, "system_prompt": ""},
            task_queue="llm-chat-queue",
            id=f"chat-query-{search_input.query_id}",
        )

        result = SearchResult(
            query_id=search_input.query_id,
            query=search_input.query,
            answer=llm_answer,
            tenant_id=search_input.tenant_id,
            chunks=chunks,
        )

        return result
