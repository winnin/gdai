from __future__ import annotations

from fastapi import HTTPException, status

from src.api.repository.repository import SearchRepository
from src.api.services.search_service import SearchService
from src.shared.embedding_model import EmbeddingModelFactory
from src.shared.llm_model import LLMModelFactory
from src.shared.logger import logger


async def get_search_service():
    """
    Initialize and return a SearchService instance with all dependencies.
    Raises HTTPException if initialization fails.
    """
    try:
        embedding_model = await EmbeddingModelFactory.create()
        llm_model = await LLMModelFactory.create()
        search_repository = SearchRepository()
        search_service = SearchService(
            llm_model=llm_model,
            embedding_model=embedding_model,
            repository=search_repository,
        )
        return search_service
    except Exception as e:
        logger.critical(f"Failed to initialize search components: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize search service",
        )
