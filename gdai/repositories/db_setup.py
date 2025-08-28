from gdai.repositories.sqlalchemy import Base, engine


async def setup_database():
    from .models import ChunkModel, DocumentModel, QueryChunkLinkModel, QueryModel  # noqa: F401

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


async def reset_database():
    # Confirmação de segurança
    confirm = input("Attention: This will DELETE ALL TABLES and recreate them. Type 'YES' to confirm: ")
    if confirm != "YES":
        print("Operation canceled.")
        return

    async with engine.begin() as conn:
        print("Deleting all tables...")

        # 1. Drop all defined tables
        await conn.run_sync(Base.metadata.drop_all)

        # 2. Drop any pgvector indexes (optional, usually drop_all removes them)
        try:
            await conn.exec_driver_sql("DROP INDEX IF EXISTS idx_chunk_hnsw")
        except Exception as e:
            print(f"Problems to remove index idx_chunk_hnsw: {e}")

        print("Tables deleted successfully!")


if __name__ == "__main__":
    import asyncio
    import sys

    if len(sys.argv) < 2:
        print("Uso: python -m gdai.repositories.sqlalchemy [setup|reset]")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "setup":
        asyncio.run(setup_database())
    elif command == "reset":
        asyncio.run(reset_database())
    else:
        print(f"Unknown command: {command}")
        print("Available commands: setup, reset")
