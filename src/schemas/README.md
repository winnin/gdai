# schemas

This folder contains Pydantic models and data validation schemas for the application.

## Purpose

- Defines the structure of data exchanged between components and APIs.
- Centralizes validation logic for requests and responses.

## How to add a new schema

1. Create a new Python file (e.g., `my_schema.py`).
2. Define your Pydantic model(s) in the new file.
3. Import and use your schema in the relevant API or service.

**Example:**

- To add a schema for a new entity, create `my_entity.py` and define your Pydantic model.
