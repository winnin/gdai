# GDAI: Multi-Tenant Vector Store with Auditable Semantic Search

GDAI is an open-source platform designed to provide a robust, multi-tenant vector store with advanced document processing and semantic search capabilities. It leverages Retrieval-Augmented Generation (RAG) and other semantic techniques to deliver accurate, auditable answers, all with full source traceability.

[![Tests](https://github.com/winnin/gdai/actions/workflows/tests.yml/badge.svg)](https://github.com/winnin/gdai/actions/workflows/tests.yml)
[![Pre-commit](https://github.com/winnin/gdai/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/winnin/gdai/actions/workflows/pre-commit.yml)
[![codecov](https://codecov.io/gh/winnin/gdai/branch/main/graph/badge.svg)](https://codecov.io/gh/winnin/gdai)
![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)

## Purpose

- **Multi-Tenant Vector Store:** Manage isolated data and search spaces for multiple organizations or users.
- **Semantic Document Processing:** Go beyond RAG by incorporating various semantic approaches for document understanding and retrieval.
- **Auditable Answers:** Every answer is traceable to its source, ensuring transparency and trust.
- **Flexible Integration:** Designed to be easily integrated into existing data pipelines and applications.

## Key Features

- **Tenant Management:** Isolate data and search for different clients or projects.
- **Document Ingestion:** Process and embed documents from various formats (PDF, Markdown, etc.).
- **Semantic Search:** Use vector similarity and advanced semantic techniques to retrieve relevant information.
- **Retrieval-Augmented Generation (RAG):** Combine retrieval with generative models for context-aware answers.
- **Source Traceability:** Every answer includes references to the original documents and locations.
- **API-First:** RESTful API for easy integration.
- **Auditing:** Built-in mechanisms to audit and review the provenance of answers.

## Getting Started

### Prerequisites

- Python 3.11+
- Docker (optional, for containerized deployment)
- PostgreSQL with pgvector extension
- RabbitMQ (for background tasks)

### Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/winnin/gdai.git
   cd gdai
   ```

2. Create a virtual environment and install dependencies using [uv](https://github.com/astral-sh/uv):

   ```sh
   uv venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   uv sync
   ```

3. Setup project configurations:

   ```sh
   task configure-dev
   ```

4. Start PostgreSQL (with pgvector), MinIO and Temporal using docker-compose:

   ```sh
   docker-compose up
   ```

5. Create your `.env` file:

   > Copy `.env.example` to `.env` and adjust as needed.

6. Run GDAI in development mode:

   ```sh
   task run
   ```

7. Access the API documentation (Swagger UI):

   > **Link:** http://localhost:8000/docs

### Querying

Use the API to perform semantic search and retrieve answers with source references.

## Temporal Workflows

This project uses Temporal for background processing pipelines.

- Queues:

  - `process-document-queue`: document extraction and chunking
  - `embedding-text-queue`: text embedding
  - `llm-queue`: conversational LLM
  - `search-on-documents-queue`: semantic search across documents

- Start Temporal server (dev) and UI are provided by `docker-compose` (ports `7233`, `8233`).

- Run workers:

```sh
# All workers (recommended during development)
task temporal:all

# Or individually
task temporal:extract
task temporal:embed
task temporal:llm
task temporal:search
```

Ensure the Temporal server is up before starting workers. The workers connect to `localhost:7233` by default.

## Documentation

- [Contributing](docs/contributing.md)
- [Code of Conduct](docs/code_of_conduct.md)
- [About](docs/about.md)
- [Changelog](CHANGELOG.md)
- [Roadmap](ROADMAP.md)

## Community & Contributing

We welcome contributions! Please read the [contributing guidelines](docs/contributing.md) and [code of conduct](docs/code_of_conduct.md) before submitting issues or pull requests.

## License

This project is licensed under the MIT License.
