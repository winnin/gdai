# from src.actor.extractor.actor import document_extractor
from __future__ import annotations

from gdai.background_tasks.embedding_background_task import embedding_document

if __name__ == "__main__":
    # Example usage
    document_data = {
        "document_path": "/home/fabricio/projects/g-dai/DOC_FOLDER/winnin1/arte_guerra.pdf",
        "tenant_id": "winnin1",
    }
    # document_data = {"document_name": "senhor_dos_aneis.pdf", "tenant_id": "tenant_321"}
    # document_data = {"document_name": "document.pdf", "tenant_id": "tenant_321"}
    # document_extractor(document_data)
    # document_extractor.send(document_data)
    embedding_document(
        {
            "document_path": "document_path",
            "tenant_id": "winnin1",
            "document_id": "3609b398-ee18-47c6-bf68-7c55d03d61cf",
        }
    )
    # embedding_document({"document_name": "arte_guerra.pdf.json"})
    # embedding_document.send({"document_name": "arte_guerra.pdf.json"} )
