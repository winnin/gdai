from __future__ import annotations

from contextlib import asynccontextmanager

import asyncpg
from pgvector.asyncpg import register_vector

from src.shared.conf import Config


class PGVectorDatabase:
    """
    A class for interacting with a PostgreSQL database using pgvector extension.

    This class manages database connections using a connection pool and provides
    methods for obtaining connections with the pgvector extension registered.

    Attributes:
        _pool (asyncpg.Pool): Singleton connection pool for database interactions.
    """

    _pool = None

    @classmethod
    async def create_connection_pool(cls):
        """
        Create a new connection pool to the PostgreSQL database.

        This method establishes a new pool of connections to the PostgreSQL database
        using the configuration parameters from the Config class.

        Returns:
            asyncpg.Pool: A newly created connection pool.

        Raises:
            asyncpg.PostgresError: If connecting to the database fails.
        """
        pool = await asyncpg.create_pool(
            user=Config.db.PGVECTOR_USER,
            password=Config.db.PGVECTOR_PASSWORD,
            database=Config.db.PGVECTOR_DATABASE,
            host=Config.db.PGVECTOR_HOST,
            port=Config.db.PGVECTOR_PORT,
            min_size=Config.db.PGVECTOR_MIN_POOL_CONNECTIONS,
            max_size=Config.db.PGVECTOR_MAX_POOL_CONNECTIONS,
        )
        return pool

    @classmethod
    async def get_connection_pool(cls):
        """
        Get or create a connection pool to the pgvector database.

        This method returns the existing connection pool if it's available,
        or creates a new one if it doesn't exist or is closed.

        Returns:
            asyncpg.Pool: The connection pool instance.
        """
        if cls._pool is None or cls._pool._closed:
            cls._pool = await cls.create_connection_pool()
        return cls._pool

    @classmethod
    @asynccontextmanager
    async def get_connection(cls):
        """
        Get a connection from the connection pool with pgvector extension registered.

        This asynchronous context manager acquires a connection from the pool,
        registers the pgvector extension, and ensures the connection is properly
        released back to the pool when done.

        Yields:
            asyncpg.Connection: A database connection with pgvector extension registered.

        Example:
            ```python
            async with PGVectorDatabase.get_connection() as conn:
                result = await conn.fetch("SELECT * FROM vector_table")
            ```
        """
        pool = await cls.get_connection_pool()
        conn = await pool.acquire()
        await register_vector(conn)
        try:
            yield conn
        finally:
            await pool.release(conn)
