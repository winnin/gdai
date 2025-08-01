from gdai.config.settings import Config

from .base_repository import BaseRepository  # noqa: F401


class RepositoryFactory:
    @staticmethod
    def get_repository():
        db_backend = Config.db.DATABASE
        if db_backend == "pgvector":
            from gdai.repositories.pgvector_repository import PGVectorRepository

            return PGVectorRepository()

        else:
            raise ValueError(f"Unsupported database backend: {db_backend}")
