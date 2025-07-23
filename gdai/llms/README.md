# llms

This folder contains logic for integrating with different Large Language Models (LLMs).

## Purpose

- Provides a standard interface for LLMs.
- Supports multiple LLM providers (e.g., OpenAI).

## How to add a new LLM

1. Create a new Python file (e.g., `deepseek.py`).
2. Inherit from the base LLM class in `base_llm.py`.
3. Implement the required methods for your LLM provider.

**Example:**

- To add a DeepSeek LLM, create `deepseek.py` and extend the class defined in `base_llm.py`.
