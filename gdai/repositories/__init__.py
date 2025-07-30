from gdai.config.settings import Config


class RepositoryFactory:
    @staticmethod
    def get_repository():
        db_backend = Config.db.DATABASE
        if db_backend == "pgvector":
            from gdai.repositories.pgvector_repository import PGVectorRepository

            return PGVectorRepository()

        else:
            raise ValueError(f"Unsupported database backend: {db_backend}")
