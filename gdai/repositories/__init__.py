from gdai.commons.settings import get_settings

from .base_repository import BaseRepository  # noqa: F401


class RepositoryFactory:
    @staticmethod
    def get_repository():
        settings = get_settings()
        db_backend = settings.database.database
        if db_backend == "pgvector":
            from gdai.repositories.pgvector_repository import PGVectorRepository

            return PGVectorRepository()

        else:
            raise ValueError(f"Unsupported database backend: {db_backend}")
