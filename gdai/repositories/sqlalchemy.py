from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from gdai.commons.config import Config

user = Config.db.PGVECTOR_USER
password = Config.db.PGVECTOR_PASSWORD
database = Config.db.PGVECTOR_DATABASE
host = Config.db.PGVECTOR_HOST
port = Config.db.PGVECTOR_PORT
min_size = Config.db.PGVECTOR_MIN_POOL_CONNECTIONS
max_size = Config.db.PGVECTOR_MAX_POOL_CONNECTIONS


DATABASE_URL = (
    f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"  # TODO: change to accept any possible database.
)

engine = create_async_engine(DATABASE_URL, echo=False, pool_size=min_size, max_overflow=max_size - min_size)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()
