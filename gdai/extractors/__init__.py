from .pdf_extractor import PDFExtractor  # noqa: F401


class ExtractorFactory:
    """Factory class to create extractor based on the type."""

    @staticmethod
    def get_extractor(extractor_type: str):
        """Get a chunker instance based on the type."""
        if extractor_type == "pdf":
            return PDFExtractor()
        else:
            raise ValueError(f"Unknown extractor type: {extractor_type}")
