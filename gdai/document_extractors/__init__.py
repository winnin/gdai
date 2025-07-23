from gdai.config.settings import Config
from gdai.document_extractors.pdf_extractor import DoclingPDFExtractor, PyMuPDFExtractor


class DocumentExtractorFactory:
    @staticmethod
    def get_extractor():
        extractor_backend = getattr(Config.extractor, "EXTRACTOR", "docling").lower()
        if extractor_backend == "pymupdf":
            return PyMuPDFExtractor()
        elif extractor_backend == "docling":
            return DoclingPDFExtractor()
        else:
            raise ValueError(f"Unsupported document extractor backend: {extractor_backend}")
