# GDAI Documentation

Welcome to the documentation for **GDAI**, a multi-tenant vector store with advanced semantic search and auditable answer capabilities.

## What is GDAI?
GDAI is an open-source platform that enables organizations to:
- Store and manage document embeddings in a vector database.
- Support multiple tenants (organizations, teams, or projects) with isolated data.
- Use semantic search and Retrieval-Augmented Generation (RAG) to answer questions based on ingested documents.
- Ensure every answer is auditable and traceable to its original source.

## Key Features
- **Multi-Tenant Management**: Isolate data and search for different clients.
- **Semantic Search**: Retrieve information using vector similarity and advanced semantic techniques.
- **RAG and Beyond**: Combine retrieval with generative models and other semantic approaches.
- **Auditable Answers**: Every answer includes references to the source documents.
- **API-First**: RESTful API for integration.

## Getting Started
- [Installation](contributing.md#installation)
- [Usage](contributing.md#usage)
- [API Reference](about.md)

## Learn More
- [Contributing](contributing.md)
- [Code of Conduct](code_of_conduct.md)
- [About the Project](about.md)

---

# GDAI - Generative Document AI

GDAI is a containerized, AI-powered application that leverages a set of specialized services to provide semantic search, secure user authentication, and a scalable API. The application uses Docker Compose for local development and production deployment, ensuring all services work together seamlessly.

## 1. Configuration

### Environment Variables (.env)

The application uses a `.env` file for configuration. Below are the main keys you must set:

```
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

---

## 2. Deployment & Running

### Local Development

1. **Install Docker and Docker Compose** (if not already installed).
2. **Start all services:**
   ```bash
   docker-compose up --build
   ```
   Or in detached mode:
   ```bash
   docker-compose up -d
   ```

## 3. API Usage

### Search Query Endpoint

- **POST** `/search/query`
- **Request Body:**
  ```json
  {
    "tenant_id": "string",
    "query_id": "string",
    "query_text": "string",
    "chunks_limit": 100
  }
  ```
- **Response:**
  ```json
  {
    "message": "string",
    "query_id": "string",
    "status": "success",
    "list_chunks": [ ... ]
  }
  ```

### Document Upload Endpoint

- **POST** `/search/document/upload`
- **Form Data:**
  - `tenant_id`: string
  - `document`: file (PDF, etc)
- **Response:**
  ```json
  {
    "message": "Document <filename> uploaded and queued for processing",
    "document_name": "<filename>",
    "tenant_id": "<tenant_id>",
    "status": "pending"
  }
  ```

---

## 4. How to Use

- **Upload a document** via `/search/document/upload` (multipart form-data).
- **Submit a search query** via `/search/query` (JSON body).
- Results will be based on the processed documents for the given tenant.

---


## 5. Contributing

- Fork the repository, create a feature branch, and submit a pull request.
- Please document new endpoints and configuration options.

---

## 6. License

- See [LICENSE](LICENSE) for details.

Happy coding!
