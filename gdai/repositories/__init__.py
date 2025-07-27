from gdai.config.settings import Config


class RepositoryFactory:
    @staticmethod
    def get_repository():
        db_backend = getattr(Config.db, "DATABASE", "pgvector").lower()
        if db_backend == "pgvector":
            from gdai.repositories.pgvector import PGVectorRepository

            return PGVectorRepository()

        else:
            raise ValueError(f"Unsupported database backend: {db_backend}")
