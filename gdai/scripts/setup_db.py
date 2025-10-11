"""Database setup script - creates tables and indexes."""

import asyncio

from gdai.repositories.database import DatabaseManager
from gdai.repositories.sqlalchemy import Base


async def setup_database():
    """Create all database tables and indexes."""
    # Import models to ensure they're registered with Base
    from gdai.repositories.models import (  # noqa: F401
        ChunkModel,
        DocumentModel,
        QueryChunkLinkModel,
        QueryModel,
    )

    try:
        engine = DatabaseManager.get_engine()

        async with engine.begin() as conn:
            # 1. Create pgvector extension
            await conn.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS vector")
            print("✓ pgvector extension created/verified")

            # 2. Create all tables
            await conn.run_sync(Base.metadata.create_all)
            print("✓ All tables created successfully!")

            # 3. Create HNSW index for similarity searches
            await conn.exec_driver_sql(
                """
                CREATE INDEX IF NOT EXISTS idx_chunk_hnsw ON chunk
                USING hnsw (embedding vector_cosine_ops)
                WITH (
                    m = 16,              -- Max connections per node (16-48)
                    ef_construction = 64 -- Precision during construction (40-200)
                );
                """
            )
            print("✓ Vector index (HNSW) created successfully!")

        print("\n✅ Database setup completed successfully!")

    except Exception as e:
        print(f"\n❌ Error setting up database: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(setup_database())
