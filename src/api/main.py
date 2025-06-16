from __future__ import annotations

import uvicorn
from fastapi import FastAPI

from src.api.routers.document import router as document_router
from src.api.routers.search import router as search_router

# Create FastAPI app
app = FastAPI(
    title="G-DAI Search API",
    description="API for document search using LLM and embeddings",
    version="1.0.0",
)

# Include the search and document routers
app.include_router(search_router)
app.include_router(document_router)


# Default route
@app.get("/")
async def root():
    return {"status": "ok", "message": "G-DAI Search API is running"}


# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "src.api.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
