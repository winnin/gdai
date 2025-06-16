from __future__ import annotations


class InvalidAPIKeyException(Exception):
    """
    Exception raised when an invalid API key is provided.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        super().__init__(f"Invalid API key provided: {api_key}")


class InvalidDocumentContentException(Exception):
    """
    Exception raised when a document is invalid.
    """

    def __init__(self, document_id: str):
        self.document_id = document_id
        super().__init__(f"Invalid document content for document ID: {document_id}")


class InsertDocumentException(Exception):
    """
    Exception raised when inserting an object into a collection fails.
    """

    def __init__(self, document_id: str, collection_name: str):
        self.document_id = document_id
        self.collection_name = collection_name
        super().__init__(
            f"Failed to insert document ID {document_id} into collection {collection_name}"
        )
