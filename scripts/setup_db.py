from gdai.repositories.sqlalchemy import Base, engine


async def setup_database():
    from gdai.repositories.models import ChunkModel, DocumentModel, QueryChunkLinkModel, QueryModel  # noqa: F401

    try:
        async with engine.begin() as conn:
            # 1. create  pgvector extension
            await conn.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS vector")

            # 2. create all tables
            await conn.run_sync(Base.metadata.create_all)
            print("Tables created successfully!")

            # 3. Criar índice IVFFLAT para pesquisas por similaridade
            await conn.exec_driver_sql("""
            CREATE INDEX idx_chunk_hnsw ON chunk
            USING hnsw (embedding vector_cosine_ops)
            WITH (
                    m = 16, -- Max number of connections per node (16-48)
                    ef_construction = 64 -- Precision during construction (40-200)
            );""")

            print("Vector index successfully created!")
    except Exception as e:
        print(f"Error creating tables: {e}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(setup_database())
