"""Database connection manager for async SQLAlchemy operations."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from gdai.commons.settings import get_settings


class DatabaseManager:
    """Singleton manager for database engine lifecycle.

    This class manages the SQLAlchemy async engine lifecycle to ensure
    proper connection pooling and event loop compatibility.
    """

    _engine: AsyncEngine | None = None
    _session_factory: sessionmaker | None = None

    @classmethod
    def get_engine(cls) -> AsyncEngine:
        """Get or create the database engine.

        Returns:
            AsyncEngine: The SQLAlchemy async engine instance.
        """
        if cls._engine is None:
            cls._engine = cls._create_engine()
        return cls._engine

    @classmethod
    def _create_engine(cls) -> AsyncEngine:
        """Create a new database engine with configuration from Settings.

        Returns:
            AsyncEngine: New SQLAlchemy async engine.
        """
        settings = get_settings()
        db_config = settings.database

        database_url = db_config.get_url()
        min_size = db_config.min_pool_connections
        max_size = db_config.max_pool_connections

        return create_async_engine(database_url, echo=False, pool_size=min_size, max_overflow=max_size - min_size)

    @classmethod
    def get_session_factory(cls) -> sessionmaker:
        """Get or create the session factory.

        Returns:
            sessionmaker: SQLAlchemy session factory.
        """
        if cls._session_factory is None:
            engine = cls.get_engine()
            cls._session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        return cls._session_factory

    @classmethod
    async def create_session(cls) -> AsyncSession:
        """Create a new database session.

        Returns:
            AsyncSession: New SQLAlchemy async session.

        Usage:
            async with await DatabaseManager.create_session() as session:
                # Use session
                pass
        """
        factory = cls.get_session_factory()
        return factory()

    @classmethod
    async def dispose(cls) -> None:
        """Dispose of the engine and clear cached instances.

        This is primarily useful for testing to ensure clean state between tests.
        """
        if cls._engine is not None:
            await cls._engine.dispose()
            cls._engine = None
            cls._session_factory = None

    @classmethod
    async def health_check(cls) -> bool:
        """Check if database connection is healthy.

        Returns:
            bool: True if database is accessible, False otherwise.
        """
        try:
            async with await cls.create_session() as session:
                await session.execute("SELECT 1")
                return True
        except Exception:
            return False
