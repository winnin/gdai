from __future__ import annotations

from abc import ABC, abstractmethod

from gdai.schemas import RawDocument


class DocumentExtractor(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def extract_document_data(self, tenant_id: str, document_path: str) -> RawDocument:
        """Extract text from a document."""
        pass
