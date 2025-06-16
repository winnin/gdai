# G-DAI: Multi-Tenant Vector Store with Auditable Semantic Search

G-DAI is an open-source platform designed to provide a robust, multi-tenant vector store with advanced document processing and semantic search capabilities. It leverages Retrieval-Augmented Generation (RAG) and other semantic techniques to deliver accurate, auditable answers, always referencing the original sources of information.

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
- Python 3.12+
- Docker (optional, for containerized deployment)
- PostgreSQL with pgvector extension

### Installation

Clone the repository:
```bash
git clone https://github.com/your-org/g-dai.git
cd g-dai
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Or use Docker Compose:
```bash
docker-compose up --build
```

### Configuration
- Edit `pyproject.toml` and `mkdocs.yml` for project settings.
- Set up your database and environment variables as needed.

### Running the API
```bash
python -m src.api.main
```

### Ingesting Documents
Place your documents in the `DOC_FOLDER/raw/` directory. Use the provided scripts or API endpoints to process and embed them.

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
