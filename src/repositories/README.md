# repositories

This folder contains data access logic for interacting with databases and storage backends.

## Purpose

- Encapsulates all database operations and queries.
- Supports multiple storage backends (e.g., pgvector, turso).

## How to add a new repository

1. Create a new Python file (e.g., `my_repository.py`).
2. Inherit from the base repository class in `base.py`.
3. Implement the required data access methods.

**Example:**

- To add a new backend, create `my_backend.py` and extend the base repository class.
