"""FastAPI application factory for GDAI."""

from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from gdai.api.routers import documents, health, queries
from gdai.commons.exceptions import GDAIException
from gdai.commons.logger import logger

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    """Application lifespan manager.

    Handles startup and shutdown events for the FastAPI application.

    Args:
        app: FastAPI application instance (required by FastAPI but not used).
    """
    # Startup
    logger.info("Starting GDAI API server...")

    # TODO: Initialize Temporal client connection
    # temporal_client = await connect_temporal_client()
    # app.state.temporal_client = temporal_client

    yield

    # Shutdown
    logger.info("Shutting down GDAI API server...")

    # TODO: Close Temporal client connection
    # if hasattr(app.state, 'temporal_client'):
    #     await app.state.temporal_client.close()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application instance.
    """
    app = FastAPI(
        title="GDAI API",
        description="Document management and query API using LLM and vector embeddings",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all incoming requests with timing information."""
        start_time = time.time()

        # Log request
        client = request.client.host if request.client else "unknown"
        logger.info(f"Request started: {request.method} {request.url.path} from {client}")

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log response
        logger.info(
            f"Request completed: {request.method} {request.url.path} - "
            f"Status: {response.status_code} - Duration: {duration:.3f}s"
        )

        return response

    # Exception handlers
    @app.exception_handler(GDAIException)
    async def gdai_exception_handler(request: Request, exc: GDAIException):  # noqa: ARG001
        """Handle GDAI custom exceptions.

        Args:
            request: The incoming request.
            exc: The GDAI exception.

        Returns:
            JSONResponse: Error response with appropriate status code.
        """
        logger.error(f"GDAI Exception: {exc.code} - {exc.message}", extra={"code": exc.code, "details": exc.details})

        # Map exception codes to HTTP status codes
        status_code_map = {
            "DOCUMENT_NOT_FOUND": status.HTTP_404_NOT_FOUND,
            "QUERY_NOT_FOUND": status.HTTP_404_NOT_FOUND,
            "CHUNK_NOT_FOUND": status.HTTP_404_NOT_FOUND,
            "FILE_NOT_FOUND": status.HTTP_404_NOT_FOUND,
            "DOCUMENT_ALREADY_EXISTS": status.HTTP_409_CONFLICT,
            "INVALID_INPUT": status.HTTP_400_BAD_REQUEST,
            "UNAUTHORIZED": status.HTTP_401_UNAUTHORIZED,
            "FORBIDDEN": status.HTTP_403_FORBIDDEN,
        }

        status_code = status_code_map.get(exc.code, status.HTTP_500_INTERNAL_SERVER_ERROR)

        return JSONResponse(status_code=status_code, content=exc.to_dict())

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle request validation errors.

        Args:
            request: The incoming request.
            exc: The validation error.

        Returns:
            JSONResponse: Error response with validation details.
        """
        logger.warning(f"Validation error: {request.method} {request.url.path}", extra={"errors": exc.errors()})

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": {"errors": exc.errors()},
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions.

        Args:
            request: The incoming request.
            exc: The exception.

        Returns:
            JSONResponse: Generic error response.
        """
        logger.exception(f"Unexpected error: {request.method} {request.url.path}", exc_info=exc)

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "details": {"error": str(exc)},
            },
        )

    # Include routers
    app.include_router(health.router, tags=["health"])
    app.include_router(documents.router, prefix="/api/v1", tags=["documents"])
    app.include_router(queries.router, prefix="/api/v1", tags=["queries"])

    # Root endpoint
    @app.get("/", summary="Root endpoint", tags=["root"])
    async def root():
        """Root endpoint returning API information."""
        return {"name": "GDAI API", "version": "1.0.0", "status": "running", "docs": "/docs"}

    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    # Run the application
    uvicorn.run("gdai.api.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
