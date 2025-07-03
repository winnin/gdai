from __future__ import annotations

from fastapi import HTTPException, status

from src.config.logger import logger
from src.embeddings import EmbeddingFactory
from src.llms import LLMFactory
from src.repositories import RepositoryFactory
from src.services.search import SearchService


async def get_search_service():
    """Initialize and return a SearchService instance with all dependencies.
    Raises HTTPException if initialization fails.
    """
    try:
        embedding_model = await EmbeddingFactory.get_embedding()
        llm_model = await LLMFactory.get_llm()
        search_repository = RepositoryFactory.get_repository().search
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
