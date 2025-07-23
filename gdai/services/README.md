# services

This folder contains the business logic and service layer of the application.

## Purpose

- Implements core application logic and orchestrates interactions between repositories, LLMs, embeddings, and background tasks.
- Provides reusable service classes for different features.

## How to add a new service

1. Create a new Python file (e.g., `my_service.py`).
2. Implement your service class, following the structure of existing services.
3. Use dependency injection to access repositories or other services as needed.

**Example:**

- To add a new service for analytics, create `analytics.py` and implement your service class.
