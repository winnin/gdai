from gdai.config.settings import Config


class RepositoryBundle:
    def __init__(self, document, search):
        self.document = document
        self.search = search


class RepositoryFactory:
    @staticmethod
    def get_repository():
        db_backend = getattr(Config.db, "DATABASE", "pgvector").lower()
        if db_backend == "pgvector":
            from gdai.repositories.pgvector import PGVectorDocumentRepository, SearchRepository

            return RepositoryBundle(
                document=PGVectorDocumentRepository(),
                search=SearchRepository(),
            )
        # elif db_backend == "turso":
        #     from src.repositories.turso import DocumentRepository, SearchRepository

        #     return RepositoryBundle(
        #         document=PGVectorDocumentRepository(),
        #         search=SearchRepository(),
        #     )
        else:
            raise ValueError(f"Unsupported database backend: {db_backend}")
