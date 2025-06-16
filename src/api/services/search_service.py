# The SearchService class has been moved to src/api/services/search_service.py
from __future__ import annotations

import logging

from src.shared.llm_model import LLMModel

logger = logging.getLogger("SEARCH_SERVICE")


class SearchService:
    """
    Service for handling search queries using LLM and embeddings.
    """

    __PROMPT_TEMPLATE_TO_SOLVE_QUERY = """
        You are an AI assistant that helps users find relevant information in documents.
        You will receive a query and a list of document chunks. Your task is to:

        1. Analyze the query and identify the key information needed.
        2. Evaluate which document chunks are most relevant to the query.
        3. Return a concise and accurate answer based ONLY on the relevant chunks.

        Rules:
        - Use only the information provided in the document chunks.
        - If no chunks are relevant, respond with "There is no relevant information available."
        - Keep the answer clear and concise, but ensure it fully addresses the query.
        - Do not add explanations, introductions, or notes—just the direct answer.

        Input:
        Query: {query}
        Document Chunks: {chunks}

        Answer:

    """

    def __init__(self, llm_model: LLMModel, embedding_model, repository):
        """
        Initialize the SearchService.

        Args:
            llm_model (LLMModel): The language model to use for answering queries.
            embedding_model: The embedding model for vector search.
            repository: The repository for database access.
        """
        self.llm_model = llm_model
        self.embedding_model = embedding_model
        self.repository = repository

    async def _retrieve_relevant_chunks(
        self, tenant_id: str, query_id: str, query: str, chunks_limit: int
    ):
        """
        Retrieve relevant document chunks based on the embedded query.

        Args:
            tenant_id (str): The ID of the tenant.
            query_id (str): The ID of the query.
            query (str): The query text.
            chunks_limit (int): The maximum number of chunks to retrieve.
        Returns:
            List[ChunkQueryResult]: A list of document chunks sorted by similarity.
        """
        # Generate embedding for the query
        embedded_query = (
            await self.embedding_model.generate_texts_embeddings([query])
        )[0]

        # Retrieve chunks using vector similarity search
        chunks_result = await self.repository.get_chunks_by_vector_similarity(
            tenant_id, query_id, embedded_query, chunks_limit
        )

        # Here you could add reranking logic if needed

        return chunks_result

    async def _handle_no_results(self, message_id: str):
        """
        Handle the case when no relevant chunks are found.

        Args:
            message_id (str): The ID of the message.
        Returns:
            None
        """
        await self.repository.update_message_status(message_id, "failed")
        return

    async def _process_llm_stream(self, message_id: str, prompt: str) -> str:
        """
        Process the streaming response from the LLM and store tokens.

        Args:
            message_id (str): The ID of the message.
            prompt (str): The prompt to send to the LLM.
        Returns:
            str: The full answer text from the LLM.
        """
        msg_result = ""
        async for token in self.llm_model.call_llm_stream(prompt):
            msg_result += token
        return msg_result

    async def _generate_answer(
        self, message_id: str, query: str, chunks_result
    ) -> dict:
        """
        Generate an answer using the LLM based on the query and relevant chunks.

        Args:
            message_id (str): The ID of the message.
            query (str): The query text.
            chunks_result: The relevant document chunks.
        Returns:
            dict: The generated answer and used chunks.
        """
        # Format chunks for the prompt
        chunks_text = "\n\n".join(
            [chunk_res.chunk.chunk_text for chunk_res in chunks_result]
        )

        # Prepare the prompt for the LLM
        prompt = self.__PROMPT_TEMPLATE_TO_SOLVE_QUERY.format(
            query=query, chunks=chunks_text
        )

        # Get streaming response from LLM and store tokens
        answer_text = await self._process_llm_stream(message_id, prompt)

        # Update message with final answer
        await self.repository.update_message_text_and_status(message_id, answer_text)

        if answer_text is None or "There is no relevant information" in answer_text:
            await self._handle_no_results(message_id)
            return {"msg": "There is no relevant information available.", "chunks": []}

        chunks_used = [
            {
                "document": chunk.chunk.doc_name,
                "tenant_id": chunk.chunk.tenant_id,
                "chunk_id": chunk.chunk.chunk_id,
                "text": chunk.chunk.chunk_text,
                "page_number": chunk.chunk.page_number,
            }
            for chunk in chunks_result
        ]
        return {"msg": answer_text, "chunks": chunks_used}

    async def answer_query(
        self, tenant_id: str, query_id: str, query: str, chunks_limit: int = 3
    ) -> str:
        """
        Answer a query by searching for relevant documents and generating a response.

        Args:
            tenant_id (str): The ID of the tenant.
            query_id (str): The ID of the query.
            query (str): The query text.
            chunks_limit (int): The maximum number of chunks to use.
        Returns:
            str: The answer to the query.
        """
        # create in table message a new message with the query with status pending
        message_id = await self.repository.create_message_entry(
            tenant_id, query_id, query
        )
        try:
            # retrieve the chunks from the database based on the query
            chunks_result = await self._retrieve_relevant_chunks(
                tenant_id, query_id, query, chunks_limit
            )

            if not chunks_result:  # ??????? if nothing is found is it a error or just no results? avoid answer something out of the rag
                await self._handle_no_results(message_id)
                return {
                    "msg": "There is no relevant information available.",
                    "chunks": [],
                }

            answer = await self._generate_answer(message_id, query, chunks_result)

            return answer
        except Exception as e:
            await self.repository.update_message_status(message_id, "failed")
            raise e
