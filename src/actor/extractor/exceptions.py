from __future__ import annotations


class InvalidDocumentPathFolderException(Exception):
    """
    Exception raised when the document path folder is invalid.
    """


class FileNotFoundException(Exception):
    """
    Exception raised when an invalid API key is provided.
    """


class InvalidExtractorOption(Exception):
    """
    Exception raised when an invalid extractor option is defined
    """
