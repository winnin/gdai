from gdai.repositories.sqlalchemy import Base, engine


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

    asyncio.run(reset_database())
