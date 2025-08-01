# The SearchService class has been moved to src/api/services/search_service.py
from __future__ import annotations

from gdai.api.routers.v1.types import SearchResponse
from gdai.commons.enums import SimilarityTypeEnum
from gdai.config.logger import logger
from gdai.embeddings import EmbeddingModel
from gdai.llms import LLMModel
from gdai.repositories import BaseRepository
from gdai.schemas import Chunk


class SearchService:
    """Service for handling search queries using LLM and embeddings."""

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
        - Answer always in the language of the query.

        Input:
        Query: {query}
        Document Chunks: {chunks}

        Answer:

    """

    def __init__(self, llm_model: LLMModel, embedding_model: EmbeddingModel, repository: BaseRepository):
        """Initialize the SearchService.

        Args:
            llm_model (LLMModel): The language model to use for answering queries.
            embedding_model: The embedding model for vector search.
            repository: The repository for database access.
        """
        self.llm_model = llm_model
        self.embedding_model = embedding_model
        self.repository = repository

    async def _process_llm_stream(self, prompt: str) -> str:
        """Process the streaming response from the LLM and store tokens.

        Args:
            message_id (str): The ID of the message.
            prompt (str): The prompt to send to the LLM.

        Returns:
            str: The full answer text from the LLM.
        """
        full_response = ""
        async for chunk in self.llm_model.call_llm_stream(prompt):
            full_response += chunk
        return full_response

    async def _generate_answer(self, query: str, chunks: list[Chunk]) -> str:
        """Generate an answer using the LLM based on the query and relevant chunks.

        Args:
            message_id (str): The ID of the message.
            query (str): The query text.
            chunks_result: The relevant document chunks.

        Returns:
            dict: The generated answer and used chunks.
        """
        # Format chunks for the prompt
        chunks_text = "\n\n".join([chunk.chunk for chunk in chunks])

        # Prepare the prompt for the LLM
        prompt = self.__PROMPT_TEMPLATE_TO_SOLVE_QUERY.format(query=query, chunks=chunks_text)

        # Get streaming response from LLM and store tokens
        answer_text = await self._process_llm_stream(prompt)

        if answer_text is None or "There is no relevant information" in answer_text:
            return {"msg": "There is no relevant information available."}

        return {"msg": answer_text}

    async def answer_query(self, tenant_id: str, query: str, document_ids_to_search=[], chunks_limit: int = 3) -> dict:
        """Answer a query by searching for relevant documents and generating a response.

        Args:
            tenant_id (str): The ID of the tenant.
            query (str): The query text.
            chunks_limit (int): The maximum number of chunks to use.

        Returns:
            dict: The answer to the query and the used chunks.
        """
        # insert query in database
        query_id = await self.repository.insert_query(tenant_id, query, SimilarityTypeEnum.cosine)

        # embedding query
        embedded_query = (await self.embedding_model.generate_texts_embeddings([query]))[0]
        logger.info(document_ids_to_search)
        chunks = []
        try:
            chunks = await self.repository.search_chunks_by_similarity(
                tenant_id=tenant_id,
                query_id=query_id,
                query_vector=embedded_query,
                similarity_threshold=0.1,
                limit=chunks_limit,
            )
        except ValueError as e:
            logger.error(f"Error retrieving chunks for query {query_id}: {e!s}")

        try:
            msg_result = await self._generate_answer(query=query, chunks=chunks)
        except Exception as e:
            logger.error(f"Error generating answer for query {query_id}: {e!s}")
            raise e

        response = SearchResponse(
            tenant_id=tenant_id,
            query_id=str(query_id),
            query=query,
            status="success",
            result=msg_result["msg"],
            list_chunks=[{"chunk_id": chunk.id, "text": chunk.chunk} for chunk in chunks],
        )
        return response
