# from src.actor.extractor.actor import document_extractor
from __future__ import annotations

from src.actor.embedding.actor import embedding_document

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
    # search_query.send({"tenant_id": "tenant_123", "query_id": "query_456", "query_text": "Quem é frodo? "})
    # search_query({"tenant_id": "tenant_321", "query_id": "query_666", "query_text": "Qual o papel de harry potter na história?"})


# faq de data
# documentação de cliente
# documetação da  NATASHA de Q&A
# memória da conversação
# migrar embedding do cohere do gemini
# processar vídeo de UGC mais importantes
# verificar endpoint de age/gender
# https://ai.google.dev/gemini-api/docs/video-understanding?hl=pt-br
