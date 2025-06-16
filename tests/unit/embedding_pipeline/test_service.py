# import os
# import pytest
# import pytest_asyncio
# from unittest.mock import AsyncMock
# from src_pipeline.service import EmbeddingActor
# from src_pipeline.schema import Document, DocumentInput
# from src_pipeline.embedding import EmbeddingModel
# from src_pipeline.repository import DocumentRepository


# class TestEmbeddingPipelineService:
#     TENANT_ID_TEST = "TestEmbeddingPipelineService_ABC1234"


#     @pytest_asyncio.fixture(scope="function")
#     async def repository(self):
#         repo =  DocumentRepository()
#         try:
#             yield repo
#         finally:
#             await repo.clean_tenant_database(tenant_id=TestEmbeddingPipelineService.TENANT_ID_TEST)


#     @pytest_asyncio.fixture
#     async def mock_embedding_model(self):
#         """
#         Mock do modelo de embedding para gerar embeddings fictícios.
#         """
#         mock_model = AsyncMock(spec=EmbeddingModel)
#         mock_model.generate_texts_embeddings = AsyncMock(
#             return_value=[[0.9] * 1536 for _ in range(10)]  # Mock de embeddings
#         )
#         return mock_model

#     @pytest.mark.asyncio
#     async def test_load_document_folder(self, repository, mock_embedding_model):
#         fixture_folder = os.path.join(os.path.dirname(__file__), "../../fixtures/embedding_pipeline")
#         valid_documents, invalid_documents_content, non_json_files = await EmbeddingActor.load_documents_from_folder(fixture_folder)
#         assert len(valid_documents) == 1
#         assert len(invalid_documents_content) == 1
#         assert len(non_json_files) == 1
#         assert valid_documents[0].doc_id == "doc1"

#     @pytest.mark.asyncio
#     async def test_process_document(self, mock_embedding_model):

#         document = Document(doc_id="TestEmbeddingPipelineService_doc1",
#                             tenant_id=self.TENANT_ID_TEST,
#                             doc_name="Test Document",
#                             pages=["Page 1", "Page 2"],
#                             embedding_model_name="test_model")
#         document_chunks = await EmbeddingActor.process_document(document, mock_embedding_model, chunk_size=5, overlap=2)
#         assert len(document_chunks) == 4

#     @pytest.mark.asyncio
#     async def test_save_document_into_db(self, repository, mock_embedding_model):
#         assert True

#     @pytest.mark.asyncio
#     async def test_delete_documents_from_db_using_folder_data(self):
#         assert True
