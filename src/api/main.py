from __future__ import annotations

import uvicorn
from fastapi import FastAPI

from src.api.routers.v1.document import router as document_router
from src.api.routers.v1.search import router as search_router

# Create FastAPI app
app = FastAPI(
    title="GDAI Search API",
    description="API for document search using LLM and embeddings",
    version="1.0.0",
)

# Include the search and document routers
app.include_router(search_router)
app.include_router(document_router)


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
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
