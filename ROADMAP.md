# Project Roadmap

This roadmap outlines the planned features and improvements for GDAI. The timeline and priorities may change based on community feedback and project needs.

## ✅ Completed (October 2024)

- [x] **Test coverage > 77%** - Achieved with 244 tests (155 unit + 89 integration)
- [x] **Different chunking strategies** - Implemented sentence and semantic chunking
- [x] **Query for specific documents** - Document management workflows implemented
- [x] **S3-compatible storage** - MinIO/AWS S3 with multi-tenant isolation
- [x] **Temporal.io workflows** - Complete workflow orchestration
- [x] **Multi-tenant architecture** - Full tenant isolation implemented
- [x] **Comprehensive documentation** - README, SPEC, diagrams, examples
- [x] **CI/CD pipeline** - GitHub Actions with 5 workflows
- [x] **Coverage badge automation** - Auto-updating coverage badge

## 🚀 In Progress (Q4 2024)

- [ ] **REST API with FastAPI** - Expose workflows via HTTP endpoints
- [ ] **Authentication & Authorization** - JWT, OAuth2, RBAC
- [ ] **Rate limiting** - Protect APIs from abuse
- [ ] **Production deployment** - Kubernetes manifests, Dockerfile
- [ ] **Monitoring & Observability** - Prometheus, Grafana, OpenTelemetry

## 📅 Q1 2025

- [ ] **OpenAI Embeddings** - Alternative to Cohere
- [ ] **Image Extractor (OCR)** - Support for images in documents
- [ ] **PPT Extractor** - PowerPoint document support
- [ ] **DOCX Extractor** - Word document support
- [ ] **Rerank RAG results** - Improve search quality
- [ ] **Hybrid search** - Combine keyword + semantic search
- [ ] **API compatible with OpenAI's vector store** - Drop-in replacement

## 📅 Q2 2025

- [ ] **MCP interface** - Model Context Protocol support
- [ ] **Support for embedding images** - Visual content embeddings
- [ ] **Support for embedding tables** - Structured data embeddings
- [ ] **Turso as a repository option** - SQLite edge database
- [ ] **Support to REDIS as a broker** - Alternative message broker
- [ ] **Document versioning** - Track document changes over time
- [ ] **Feedback loop** - User feedback (thumbs up/down)

## Future Ideas

- [ ] Knowledge capabilities on search
- [ ] Integration with cloud storage providers (AWS S3, GCP, Azure)
- [ ] Benchmark on datasets (compare with solutions like Cognee)
- [ ] Handle temporal aspects (documents contradicting each other when written at different times)
- [ ] How to converge RAG to become a "long-term memory"
- [ ] Explainability capabilities on reasoning (link term memory)

---

_This roadmap is subject to change. Contributions and suggestions are welcome!_
