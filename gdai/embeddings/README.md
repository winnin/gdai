# embeddings

This folder contains modules for generating and managing text embeddings using different providers.

## Purpose

- Provides a standard interface for embedding models.
- Supports multiple embedding providers (e.g., Cohere).

## How to add a new embedding model

1. Create a new Python file (e.g., `my_embedding.py`).
2. Inherit from the base embedding class in `base.py`.
3. Implement the required methods for your embedding provider.

**Example:**

- To add a DeepSeek embedding, create `deepseek.py` and extend the base class.
