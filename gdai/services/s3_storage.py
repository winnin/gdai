"""S3/MinIO storage service for file management.

This module provides a service layer for interacting with S3-compatible storage
(MinIO in development, AWS S3 in production) for document storage and retrieval.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import BinaryIO

import boto3
from botocore.exceptions import ClientError

from gdai.commons.settings import get_settings

logger = logging.getLogger(__name__)


class S3StorageService:
    """Service for managing files in S3/MinIO storage.

    This service handles all interactions with S3-compatible storage including:
    - File uploads with tenant isolation using prefixes
    - File downloads to local temporary storage
    - File deletion
    - Bucket management

    Files are organized by tenant: {bucket}/{tenant_id}/{filename}
    """

    def __init__(self):
        """Initialize S3 storage service with settings from environment."""
        settings = get_settings()

        self.bucket = settings.s3.bucket
        self.endpoint = settings.s3.endpoint
        self.use_ssl = settings.s3.use_ssl

        # Initialize boto3 S3 client
        self.client = boto3.client(
            "s3",
            endpoint_url=self.endpoint,
            aws_access_key_id=settings.s3.access_key,
            aws_secret_access_key=settings.s3.secret_key,
            region_name=settings.s3.region,
            use_ssl=self.use_ssl,
        )

        # Ensure bucket exists
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self) -> None:
        """Ensure the configured bucket exists, create if it doesn't."""
        try:
            self.client.head_bucket(Bucket=self.bucket)
            logger.info(f"Bucket '{self.bucket}' exists")
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                logger.info(f"Creating bucket '{self.bucket}'")
                self.client.create_bucket(Bucket=self.bucket)
            else:
                logger.error(f"Error checking bucket: {e}")
                raise

    def get_s3_key(self, tenant_id: str, filename: str) -> str:
        """Generate S3 key with tenant prefix.

        Args:
            tenant_id: Tenant identifier for isolation
            filename: Name of the file

        Returns:
            S3 key in format: {tenant_id}/{filename}
        """
        return f"{tenant_id}/{filename}"

    def upload_file(self, tenant_id: str, file_path: str, object_name: str | None = None) -> str:
        """Upload a file to S3 with tenant isolation.

        Args:
            tenant_id: Tenant identifier for isolation
            file_path: Local path to the file to upload
            object_name: S3 object name (defaults to filename from file_path)

        Returns:
            S3 key of the uploaded file

        Raises:
            FileNotFoundError: If the file_path doesn't exist
            ClientError: If upload fails
        """
        if object_name is None:
            object_name = Path(file_path).name

        s3_key = self.get_s3_key(tenant_id, object_name)

        try:
            self.client.upload_file(file_path, self.bucket, s3_key)
            logger.info(f"Uploaded file to s3://{self.bucket}/{s3_key}")
            return s3_key
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except ClientError as e:
            logger.error(f"Failed to upload file: {e}")
            raise

    def upload_fileobj(self, tenant_id: str, file_obj: BinaryIO, object_name: str) -> str:
        """Upload a file object to S3 with tenant isolation.

        Args:
            tenant_id: Tenant identifier for isolation
            file_obj: File-like object to upload
            object_name: S3 object name

        Returns:
            S3 key of the uploaded file

        Raises:
            ClientError: If upload fails
        """
        s3_key = self.get_s3_key(tenant_id, object_name)

        try:
            self.client.upload_fileobj(file_obj, self.bucket, s3_key)
            logger.info(f"Uploaded file object to s3://{self.bucket}/{s3_key}")
            return s3_key
        except ClientError as e:
            logger.error(f"Failed to upload file object: {e}")
            raise

    def download_file(self, s3_key: str, local_path: str) -> None:
        """Download a file from S3 to local filesystem.

        Args:
            s3_key: S3 key of the file to download
            local_path: Local path where file should be saved

        Raises:
            ClientError: If download fails or file doesn't exist
        """
        try:
            # Ensure parent directory exists
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)

            self.client.download_file(self.bucket, s3_key, local_path)
            logger.info(f"Downloaded s3://{self.bucket}/{s3_key} to {local_path}")
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                logger.error(f"File not found in S3: {s3_key}")
            else:
                logger.error(f"Failed to download file: {e}")
            raise

    def delete_file(self, s3_key: str) -> None:
        """Delete a file from S3.

        Args:
            s3_key: S3 key of the file to delete

        Raises:
            ClientError: If deletion fails
        """
        try:
            self.client.delete_object(Bucket=self.bucket, Key=s3_key)
            logger.info(f"Deleted s3://{self.bucket}/{s3_key}")
        except ClientError as e:
            logger.error(f"Failed to delete file: {e}")
            raise

    def file_exists(self, s3_key: str) -> bool:
        """Check if a file exists in S3.

        Args:
            s3_key: S3 key of the file to check

        Returns:
            True if file exists, False otherwise
        """
        try:
            self.client.head_object(Bucket=self.bucket, Key=s3_key)
            return True
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                return False
            else:
                logger.error(f"Error checking file existence: {e}")
                raise

    def get_file_url(self, s3_key: str) -> str:
        """Get the full URL to a file in S3.

        Args:
            s3_key: S3 key of the file

        Returns:
            Full S3 URL to the file
        """
        return f"s3://{self.bucket}/{s3_key}"

    def list_files(self, tenant_id: str, prefix: str = "") -> list[str]:
        """List all files for a tenant.

        Args:
            tenant_id: Tenant identifier
            prefix: Additional prefix filter within tenant namespace

        Returns:
            List of S3 keys for files matching the criteria
        """
        tenant_prefix = f"{tenant_id}/{prefix}" if prefix else f"{tenant_id}/"

        try:
            response = self.client.list_objects_v2(Bucket=self.bucket, Prefix=tenant_prefix)

            if "Contents" not in response:
                return []

            return [obj["Key"] for obj in response["Contents"]]
        except ClientError as e:
            logger.error(f"Failed to list files: {e}")
            raise


def get_s3_storage() -> S3StorageService:
    """Get S3 storage service instance.

    Returns:
        Configured S3StorageService instance
    """
    return S3StorageService()
