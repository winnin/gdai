# api

This folder contains the main API layer of the application, including the FastAPI app, dependencies, and routers.

## Purpose

- Exposes HTTP endpoints for the application.
- Handles request validation, authentication, and routing.
- Connects the outside world to the internal services and business logic.

## How to add a new API component

1. To add a new route, create a new file in the `routers/` subfolder and define your FastAPI router there.
2. Register your new router in `app.py`.
3. If you need new dependencies, add them to `deps.py`.

**Example:**

- To add a new endpoint for document upload, create `routers/document_upload.py` and define your route logic there.
