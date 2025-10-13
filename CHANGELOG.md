# Changelog

All notable changes to this project will be documented in this file.

The format follows the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) standard.

## [Unreleased]

### Added

- Automated coverage badge that updates on every push
- Coverage badge workflow that extracts and displays real test coverage
- Comprehensive .claude/CLAUDE.md for AI-assisted development
- 5 GitHub Actions workflows (CI, PR checks, Security, Docs, Coverage)
- Mermaid diagrams in README (architecture, database, workflows)

### Changed

- Consolidated configuration from config.py to Pydantic Settings (settings.py)
- Updated badges to show accurate workflow status
- Improved documentation with 3,000+ lines across README, SPEC, ROADMAP
- Restructured test organization (flat structure: unit/ and integration/)
- Enhanced CI/CD pipeline with parallel jobs and caching

### Fixed

- MinIO container startup in GitHub Actions (manual docker run)
- Missing pydantic-settings and ruff dependencies
- PYTHONPATH configuration in CI workflows
- Code formatting issues across 3 files
- Badge URLs to correctly show workflow status

### Removed

- Obsolete config.py (replaced by settings.py)
- Old workflow files (tests.yml, pre-commit.yml, gh-pages.yml)
- Duplicate configuration code (708 lines removed)

## [0.1.0] - 2024-07-14

### Added

- First release of GDAI
- Multi-tenant vector store with complete data isolation
- Temporal.io workflow orchestration for document processing
- PostgreSQL + pgvector for vector similarity search
- S3-compatible storage (MinIO/AWS S3) with tenant isolation
- Document extraction from PDFs (PyMuPDF)
- Text chunking with multiple strategies (sentence, semantic)
- Embedding generation via Cohere embed-v4.0 (1536 dimensions)
- RAG-based question answering with OpenAI GPT-4o
- Source traceability for all answers
- Document management workflows (list, get, delete, get chunks)
- 155 unit tests + 103 integration tests (77% coverage)
- Comprehensive documentation (README, SPEC, ROADMAP)
- Docker Compose for local development
- UV package manager for fast dependency management
