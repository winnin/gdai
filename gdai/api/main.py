from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from gdai.api.routers.v1.document_router import router as document_router
from gdai.api.routers.v1.search_router import router as search_router
from gdai.background_daemons.embedding_document_daemon import EmbeddingDocumentDaemon
from gdai.background_daemons.extract_document_daemon import ExtractDocumentDaemon


@asynccontextmanager
async def lifespan(_: FastAPI):
    task1 = asyncio.create_task(ExtractDocumentDaemon().run())
    task2 = asyncio.create_task(EmbeddingDocumentDaemon().run())

    try:
        yield  # Aqui dentro, a API já está ativa
    finally:
        # Finalização (após a aplicação encerrar)
        task1.cancel()
        task2.cancel()
        try:
            await task1
            await task2
        except asyncio.CancelledError:
            print("Daemons cancelled")


# Create FastAPI app
app = FastAPI(
    title="GDAI Search API",
    description="API for document search using LLM and embeddings",
    version="1.0.0",
    lifespan=lifespan,
)

# Include the search and document routers
# app.include_router(search_router)
app.include_router(document_router, prefix="/v1", tags=["document"])
app.include_router(search_router, prefix="/v1", tags=["search"])


# Default route
@app.get("/")
async def root():
    return {"status": "ok", "message": "GDAI Search API is running"}


# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    # Run the application
    uvicorn.run("gdai.api.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
