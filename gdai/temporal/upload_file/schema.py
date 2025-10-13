"""Schema definitions for file upload workflows."""

from dataclasses import dataclass


@dataclass
class UploadFileInput:
    """Input for uploading a file to S3.

    Attributes:
        tenant_id: Tenant identifier for isolation
        file_path: Local path to the file to upload
        object_name: Optional custom name for the object in S3 (defaults to filename)
        metadata: Optional metadata to associate with the file
    """

    tenant_id: str
    file_path: str
    object_name: str | None = None
    metadata: dict[str, str] | None = None


@dataclass
class UploadFileOutput:
    """Output for file upload operation.

    Attributes:
        s3_key: S3 key of the uploaded file
        s3_url: Full S3 URL to the file
        file_size: Size of the uploaded file in bytes
        success: Whether the upload was successful
        error_message: Error message if upload failed
    """

    s3_key: str
    s3_url: str
    file_size: int
    success: bool
    error_message: str | None = None


@dataclass
class UploadFileobjInput:
    """Input for uploading a file object (in-memory) to S3.

    Attributes:
        tenant_id: Tenant identifier for isolation
        file_content: File content as bytes
        object_name: Name for the object in S3
        content_type: Optional MIME type of the file
        metadata: Optional metadata to associate with the file
    """

    tenant_id: str
    file_content: bytes
    object_name: str
    content_type: str | None = None
    metadata: dict[str, str] | None = None


@dataclass
class DeleteFileInput:
    """Input for deleting a file from S3.

    Attributes:
        s3_key: S3 key of the file to delete
    """

    s3_key: str


@dataclass
class DeleteFileOutput:
    """Output for file deletion operation.

    Attributes:
        s3_key: S3 key of the deleted file
        success: Whether the deletion was successful
        error_message: Error message if deletion failed
    """

    s3_key: str
    success: bool
    error_message: str | None = None


@dataclass
class CheckFileExistsInput:
    """Input for checking if a file exists in S3.

    Attributes:
        s3_key: S3 key of the file to check
    """

    s3_key: str


@dataclass
class CheckFileExistsOutput:
    """Output for file existence check.

    Attributes:
        s3_key: S3 key that was checked
        exists: Whether the file exists
    """

    s3_key: str
    exists: bool


@dataclass
class ListFilesInput:
    """Input for listing files in S3.

    Attributes:
        tenant_id: Tenant identifier for isolation
        prefix: Optional prefix filter within tenant namespace
    """

    tenant_id: str
    prefix: str = ""


@dataclass
class FileInfo:
    """Information about a file in S3.

    Attributes:
        s3_key: S3 key of the file
        size: Size of the file in bytes
        last_modified: Last modification timestamp
    """

    s3_key: str
    size: int
    last_modified: str


@dataclass
class ListFilesOutput:
    """Output for listing files.

    Attributes:
        files: List of file information
        total: Total number of files found
    """

    files: list[FileInfo]
    total: int
