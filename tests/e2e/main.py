from __future__ import annotations

from gdai.background_tasks.embedding_background_task import embedding_document

if __name__ == "__main__":
    # Example usage
    document_data = {
        "document_path": "/home/fabricio/projects/g-dai/DOC_FOLDER/winnin1/arte_guerra.pdf",
        "tenant_id": "fabricioo",
    }
    # document_data = {"document_name": "senhor_dos_aneis.pdf", "tenant_id": "tenant_321"}
    # document_data = {"document_name": "document.pdf", "tenant_id": "tenant_321"}
    # document_extractor(document_data)
    # document_extractor.send(document_data)
    embedding_document(
        {
            "tenant_id": "jogorpg",
            "document_id": "883a6902-5b81-4c6a-9b41-23a6cb23c054",
        }
    )
    # embedding_document({"document_name": "arte_guerra.pdf.json"})
    # embedding_document.send({"document_name": "arte_guerra.pdf.json"} )
