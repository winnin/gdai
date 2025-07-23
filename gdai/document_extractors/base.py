from __future__ import annotations

from abc import ABC, abstractmethod


class DocumentExtractor(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def extract_document_data(self, document_path: str) -> dict:
        """Extract text from a document."""
        pass
