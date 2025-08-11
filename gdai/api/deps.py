from __future__ import annotations

from fastapi import HTTPException, status

from gdai.config.logger import logger
from gdai.embeddings import EmbeddingFactory
from gdai.llms import LLMFactory
from gdai.repositories import RepositoryFactory
from gdai.services.document_service import RegisterDocumentService, SearchDocumentService
from gdai.services.search_service import SearchService


async def get_search_service():
    """Initialize and return a SearchService instance with all dependencies.
    Raises HTTPException if initialization fails.
    """
    try:
        embedding_model = await EmbeddingFactory.get_embedding()
        llm_model = await LLMFactory.get_llm()
        repository = RepositoryFactory.get_repository()
        search_service = SearchService(
            llm_model=llm_model,
            embedding_model=embedding_model,
            repository=repository,
        )
        return search_service
    except Exception as e:
        logger.critical(f"Failed to initialize search components: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize search service",
        )


async def get_search_document_service():
    """Initialize and return a DocumentService instance with all dependencies.
    Raises HTTPException if initialization fails.
    """
    try:
        repository = RepositoryFactory.get_repository()
        document_service = SearchDocumentService(repository=repository)
        return document_service
    except Exception as e:
        logger.critical(f"Failed to initialize document service: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize document service",
        )


async def get_document_insert_service():
    """Initialize and return a DocumentInsertService instance with all dependencies.
    Raises HTTPException if initialization fails.
    """
    try:
        repository = RepositoryFactory.get_repository()
        document_insert_service = RegisterDocumentService(repository=repository)
        return document_insert_service
    except Exception as e:
        logger.critical(f"Failed to initialize document insert service: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize document insert service",
        )
