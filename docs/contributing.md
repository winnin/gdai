# Contributing to GDAI

We welcome contributions from the community! Please follow these guidelines to help us maintain a high-quality project.

## Getting Started

### Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/winnin/gdai.git
   cd gdai
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

Running Dramatiq document processors

```sh
    python -m dramatiq src.extractor.actor src.embedding.actor src.search.actor
```

Running API services

```sh
    python -m src.api.main
```

Use swagger to call API

> **Link:** http://localhost:8000/docs.

## How to Contribute

- Fork the repository and create your branch from `main`.
- Write clear, concise commit messages.
- Ensure your code passes linting and tests.
- Submit a pull request with a detailed description of your changes.

## Coding Standards

- Follow PEP8 and use Ruff for linting/formatting.
- Write tests for new features and bug fixes.
- Document your code and public APIs.

## Reporting Issues

- Use GitHub Issues to report bugs or request features.
- Provide as much detail as possible, including steps to reproduce and expected behavior.

## Community

- Be respectful and follow our [Code of Conduct](code_of_conduct.md).
