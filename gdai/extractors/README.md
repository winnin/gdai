# document_extractors

This folder contains logic for extracting content from various document formats.

## Purpose

- Provides a unified interface for extracting text and metadata from documents (e.g., PDF, DOCX).
- Supports extensibility for new document types.

## How to add a new document extractor

1. Create a new Python file (e.g., `my_format_extractor.py`).
2. Inherit from the base extractor class in `base.py`.
3. Implement the required extraction methods.
4. Register your extractor if needed.

**Example:**

- To add an extractor for HTML files, create `html_extractor.py` and extend the base class.
