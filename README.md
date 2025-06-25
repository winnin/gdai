# G-DAI: Multi-Tenant Vector Store with Auditable Semantic Search

G-DAI is an open-source platform designed to provide a robust, multi-tenant vector store with advanced document processing and semantic search capabilities. It leverages Retrieval-Augmented Generation (RAG) and other semantic techniques to deliver accurate, auditable answers, al

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

### Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/your-org/g-dai.git
   cd g-dai
   ```

2. Create a virtual environment and install dependencies using uv:

   ```sh
   uv venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   uv sync --all-groups  # Installs all dependencies including test packages
   ```

3. Setup pre-commit hooks:

   ```sh
   pre-commit install
   pre-commit install --hook-type pre-push
   ```

4. Running PGVector and RabbitMQ using docker-compose

   ```sh
   docker-compose up
   ```

5. Define .env file

```sh


GDAI_LOG_LEVEL=DEBUG
GDAI_LOG_FORMAT=[%(asctime)s] [GDAI] [%(levelname)s]: %(message)s
GDAI_LOG_FILE_ENABLED=false
GDAI_LOG_FILE_PATH=PROJECT_PATH/gdai/logs/gdai.log
GDAI_LOG_FILE_MAX_SIZE_MB=10
GDAI_LOG_FILE_BACKUP_COUNT=5

RABBIT_MQ_HOST=localhost
RABBIT_MQ_PORT=5672
RABBIT_MQ_USER=rabbitmq
RABBIT_MQ_PASSWORD=rabbitmq

PGVECTOR_USER=testuser
PGVECTOR_PASSWORD=testpwd
PGVECTOR_DATABASE=vectordb
PGVECTOR_HOST=localhost
PGVECTOR_PORT=5555
PGVECTOR_MIN_POOL_CONNECTIONS=2
PGVECTOR_MAX_POOL_CONNECTIONS=10

DOCUMENT_EXTRACTOR_FOLDER_SOURCE_PATH=PROJECT_PATH/gdai/DOC_FOLDER/raw
DOCUMENT_EXTRACTOR_FOLDER_TARGET_PATH=/PROJECT_PATH/gdai/DOC_FOLDER/extracted
DOCUMENT_EXTRACTOR_MAX_FILE_SIZE_MB=100
DOCUMENT_EXTRACTOR=docling
DOCUMENT_EXTRACTOR_MAX_RETRIES=3
DOCUMENT_EXTRACTOR_RETRY_DELAY=5
DOCUMENT_EXTRACTOR_QUEUE=extract_data

EMBEDDING_FOLDER_SOURCE_PATH=PROJECT_PATH/gdai/DOC_FOLDER/extracted
EMBEDDING_CHUNK_SIZE=1000
EMBEDDING_CHUNK_OVERLAP=10
EMBEDDING_MAX_RETRIES=3
EMBEDDING_RETRY_DELAY=5
EMBEDDING_QUEUE=embedding_documents
EMBEDDING_MAX_MEMORY_USAGE_PERCENT=90
EMBEDDING_MODEL=cohere/embed-v4.0
EMBEDDING_API_KEY=your-cohere-api-key

SEARCH_LLM_MODEL=openai/gpt-4o
SEARCH_LLM_API_KEY=your-openai-api-key
SEARCH_LLM_MAX_TOKENS=1000
SEARCH_LLM_TEMPERATURE=0.7

```

> **Note:** Replace `your-cohere-api-key` and `your-openai-api-key` with your actual API keys.

6. Running Dramatiq document processors

```sh
    python -m dramatiq src.extractor.actor src.embedding.actor src.search.actor
```

5. Running API services

```sh
    python -m src.api.main
```

6. Use swagger to call API

   > **Link:** http://localhost:8000/docs.

### Querying

Use the API to perform semantic search and retrieve answers with source references.

## Documentation

- [Project Overview](docs/index.md)
- [Contributing](docs/contributing.md)
- [Code of Conduct](docs/code_of_conduct.md)
- [About](docs/about.md)

## Community & Contributing

We welcome contributions! Please read the [contributing guidelines](docs/contributing.md) and [code of conduct](docs/code_of_conduct.md) before submitting issues or pull requests.

## License

This project is licensed under the MIT License.
