"""Database reset script - drops all tables and recreates them."""

import asyncio

from gdai.repositories.database import DatabaseManager
from gdai.repositories.sqlalchemy import Base


async def reset_database():
    """Drop all tables and recreate database schema."""
    # Safety confirmation
    confirm = input("\n⚠️  WARNING: This will DELETE ALL TABLES and data!\nType 'YES' to confirm: ")

    if confirm != "YES":
        print("❌ Operation canceled.")
        return

    try:
        engine = DatabaseManager.get_engine()

        async with engine.begin() as conn:
            print("\n🗑️  Dropping all tables...")

            # 1. Drop vector indexes first
            try:
                await conn.exec_driver_sql("DROP INDEX IF EXISTS idx_chunk_hnsw")
                print("✓ Vector index dropped")
            except Exception as e:
                print(f"⚠️  Could not drop index idx_chunk_hnsw: {e}")

            # 2. Drop all tables
            await conn.run_sync(Base.metadata.drop_all)
            print("✓ All tables dropped")

        print("\n✅ Database reset completed!")
        print("\n💡 Run 'python gdai/scripts/setup_db.py' to recreate tables.")

    except Exception as e:
        print(f"\n❌ Error resetting database: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(reset_database())
