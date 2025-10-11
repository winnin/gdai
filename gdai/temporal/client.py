"""Temporal client management."""

from __future__ import annotations

from temporalio.client import Client

from gdai.commons.logger import logger
from gdai.commons.settings import get_settings


class TemporalClientManager:
    """Singleton manager for Temporal client lifecycle.

    This class manages the Temporal client connection to ensure
    proper connection pooling and lifecycle management.
    """

    _client: Client | None = None

    @classmethod
    async def get_client(cls) -> Client:
        """Get or create the Temporal client.

        Returns:
            Client: The Temporal client instance.
        """
        if cls._client is None:
            cls._client = await cls._create_client()
        return cls._client

    @classmethod
    async def _create_client(cls) -> Client:
        """Create a new Temporal client with configuration.

        Returns:
            Client: New Temporal client.
        """
        try:
            # Get Temporal configuration
            settings = get_settings()
            temporal_config = settings.temporal
            temporal_host = temporal_config.host
            temporal_namespace = temporal_config.namespace

            logger.info(f"Connecting to Temporal at {temporal_host}, namespace: {temporal_namespace}")

            client = await Client.connect(temporal_host, namespace=temporal_namespace)

            logger.info("Successfully connected to Temporal")
            return client

        except Exception as e:
            logger.error(f"Failed to connect to Temporal: {e}")
            raise

    @classmethod
    async def close(cls) -> None:
        """Close the Temporal client connection.

        This is primarily useful for testing and graceful shutdown.
        """
        if cls._client is not None:
            await cls._client.close()
            cls._client = None
            logger.info("Temporal client connection closed")

    @classmethod
    async def health_check(cls) -> bool:
        """Check if Temporal connection is healthy.

        Returns:
            bool: True if Temporal is accessible, False otherwise.
        """
        try:
            client = await cls.get_client()
            # Try to describe the workflow service
            await client.workflow_service.get_system_info()
            return True
        except Exception as e:
            logger.warning(f"Temporal health check failed: {e}")
            return False
