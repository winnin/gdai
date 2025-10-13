# GDAI Technical Specifications

This directory contains detailed technical specifications for all components of the GDAI project.

## 📁 Specification Files

### Core Architecture

- **[overview.md](./overview.md)** - Project overview, architecture, and key features
- **[commons.md](./commons.md)** - Shared components (settings, enums, exceptions, logging)
- **[repositories.md](./repositories.md)** - Data access layer and database models
- **[services.md](./services.md)** - Business logic (extractors, chunkers, embeddings, LLMs, storage)

### Temporal.io Workflows

- **[upload-file-workflow.md](./upload-file-workflow.md)** - File upload to S3/MinIO
- **[extract-document-workflow.md](./extract-document-workflow.md)** - PDF extraction and processing
- **[embedding-texts-workflow.md](./embedding-texts-workflow.md)** - Text embedding generation
- **[document-management-workflow.md](./document-management-workflow.md)** - Document CRUD operations
- **[search-documents-workflow.md](./search-documents-workflow.md)** - Semantic search with RAG
- **[conversational-llm-workflow.md](./conversational-llm-workflow.md)** - LLM text generation

### Testing

- **[testing.md](./testing.md)** - Test strategy, structure, and coverage

## 🔄 Document Processing Flow

```
1. Upload File
   └─ upload-file-workflow.md

2. Extract Document
   └─ extract-document-workflow.md
      ├─ Uses: services.md (extractors, chunkers)
      └─ Calls: embedding-texts-workflow.md

3. Search Documents
   └─ search-documents-workflow.md
      ├─ Uses: repositories.md (vector search)
      ├─ Uses: services.md (embeddings)
      └─ Calls: conversational-llm-workflow.md

4. Manage Documents
   └─ document-management-workflow.md
      └─ Uses: repositories.md, upload-file-workflow.md
```

## 🎯 Quick Navigation

### I want to understand...

- **How files are stored** → [upload-file-workflow.md](./upload-file-workflow.md)
- **How PDFs are processed** → [extract-document-workflow.md](./extract-document-workflow.md)
- **How embeddings are generated** → [embedding-texts-workflow.md](./embedding-texts-workflow.md)
- **How search works** → [search-documents-workflow.md](./search-documents-workflow.md)
- **How RAG answers are generated** → [conversational-llm-workflow.md](./conversational-llm-workflow.md)
- **How documents are managed** → [document-management-workflow.md](./document-management-workflow.md)
- **Database schema and queries** → [repositories.md](./repositories.md)
- **External service integrations** → [services.md](./services.md)
- **Configuration and settings** → [commons.md](./commons.md)
- **Testing approach** → [testing.md](./testing.md)

### I want to implement...

- **New document type support** → [services.md](./services.md#extractorspy---document-extraction) + [extract-document-workflow.md](./extract-document-workflow.md)
- **New chunking strategy** → [services.md](./services.md#chunkerspy---text-chunking)
- **New embedding provider** → [services.md](./services.md#embeddingspy---embedding-generation)
- **New LLM provider** → [services.md](./services.md#llmspy---language-model-integration)
- **New workflow** → Follow patterns in existing workflow specs

## 📊 Architecture Layers

```
┌─────────────────────────────────────┐
│         Workflows Layer             │  ← All *-workflow.md files
│    (Temporal.io orchestration)     │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         Services Layer              │  ← services.md
│  (Business logic, integrations)    │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│       Repositories Layer            │  ← repositories.md
│     (Data access, database)        │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         Commons Layer               │  ← commons.md
│  (Settings, enums, exceptions)     │
└─────────────────────────────────────┘
```

## 🔗 Cross-References

Each specification file contains "Related Specs" section linking to other relevant specifications.

## 📝 Specification Format

Each spec includes:

1. **Location** - File system path
2. **Purpose** - What the component does
3. **Configuration** - Environment variables and settings
4. **API/Interface** - Public methods and schemas
5. **Usage Examples** - Code examples
6. **Integration Points** - How it connects to other components
7. **Error Handling** - Common errors and solutions
8. **Related Specs** - Links to other specifications

## 🚀 Getting Started

1. Start with [overview.md](./overview.md) for the big picture
2. Read [commons.md](./commons.md) to understand configuration
3. Explore workflow specs based on your use case
4. Dive into [services.md](./services.md) and [repositories.md](./repositories.md) for implementation details

## 📅 Last Updated

2025-10-13

---

For general project information, see the main [README.md](../../README.md) in the project root.
