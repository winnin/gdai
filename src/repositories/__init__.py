from src.config.settings import Config


class RepositoryBundle:
    def __init__(self, document, search):
        self.document = document
        self.search = search


class RepositoryFactory:
    @staticmethod
    def get_repository():
        db_backend = getattr(Config.db, "DATABASE", "pgvector").lower()
        if db_backend == "pgvector":
            from src.repositories.pgvector import DocumentRepository, SearchRepository

            return RepositoryBundle(
                document=DocumentRepository(),
                search=SearchRepository(),
            )
        elif db_backend == "turso":
            from src.repositories.turso import DocumentRepository, SearchRepository

            return RepositoryBundle(
                document=DocumentRepository(),
                search=SearchRepository(),
            )
        else:
            raise ValueError(f"Unsupported database backend: {db_backend}")
