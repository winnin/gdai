# from src.actor.extractor.actor import document_extractor
from __future__ import annotations

from gdai.background_tasks.embedding_chunks import embedding_document

if __name__ == "__main__":
    # Example usage
    document_data = {"document_name": "arte_guerra.pdf", "tenant_id": "tenant_321"}
    # document_data = {"document_name": "senhor_dos_aneis.pdf", "tenant_id": "tenant_321"}
    # document_data = {"document_name": "document.pdf", "tenant_id": "tenant_321"}
    # document_extractor(document_data)
    # document_extractor.send(document_data)
    # embedding_document({"document_name": "document.pdf.json"} )
    embedding_document({"document_name": "arte_guerra.pdf.json"})
    # embedding_document.send({"document_name": "arte_guerra.pdf.json"} )
