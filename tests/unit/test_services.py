import os
import uuid
from unittest.mock import AsyncMock, Mock, patch

import pytest

from gdai.chunker.base_chunker import BaseChunker
from gdai.commons.enums import ChunkTypeEnum, DocumentStatusEnum, DocumentTypeEnum
from gdai.embeddings.base_embedding import EmbeddingModel
from gdai.extractors.base_extractor import DocumentExtractor
from gdai.extractors.exceptions import FileNotFoundException
from gdai.repositories.base import BaseRepository
from gdai.schemas import Chunk, Document
from gdai.schemas.schemas import RawDocument
from gdai.services import ExtractDocumentService
from gdai.services.embedding_service import EmbeddingDocumentService


class TestExtractDocumentService:
    """Test suite for the ExtractDocumentService."""

    @pytest.fixture
    def mock_repository(self):
        """Return a mock repository for testing."""
        repository = Mock(spec=BaseRepository)
        document = Document(
            id=uuid.uuid4(),
            tenant_id="test-tenant",
            name="document_large_with_text_and_image.pdf",
            path="/home/fabricio/projects/g-dai/tests/unit/../fixtures/document_large_with_text_and_image.pdf",
            status=DocumentStatusEnum.uploaded,
        )
        repository.insert_document_and_chunks = AsyncMock(return_value=document)
        repository.save_document = AsyncMock(return_value=document)
        repository.save_chunks = AsyncMock()
        return repository

    @pytest.fixture
    def mock_extractor(self):
        """Return a mock document extractor for testing."""
        extractor = Mock(spec=DocumentExtractor)

        def mock_extract_data(tenant_id, document_path):
            filename = os.path.basename(document_path)
            return RawDocument(
                tenant_id=tenant_id,
                name=filename,
                path=document_path,
                type=DocumentTypeEnum.pdf,
                texts=[(1, "Texto de exemplo"), (2, "Mais texto")],
                tables=[(1, "Dados da tabela")],
                images=[],
            )

        extractor.extract_document_data = mock_extract_data
        return extractor

    @pytest.fixture
    def mock_chunker(self):
        """Return a mock chunker for testing."""
        chunker = Mock(spec=BaseChunker)
        chunker.chunk = Mock(return_value=[(1, "Chunk 1"), (2, "Chunk 2")])
        return chunker

    @pytest.fixture
    def document_service(self, mock_repository, mock_extractor, mock_chunker):
        """Return a ExtractDocumentService instance for testing."""
        return ExtractDocumentService(
            repository=mock_repository, document_extractor=mock_extractor, chunker=mock_chunker
        )

    @staticmethod
    def get_test_file_path(filename):
        """Get path to a test file in fixtures directory."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        fixtures_path = os.path.join(current_dir, "..", "fixtures")
        return os.path.join(fixtures_path, filename)

    @pytest.fixture
    def valid_document_data(self):
        """Return valid document data for testing."""
        return {
            "tenant_id": "test-tenant",
            "document_path": self.get_test_file_path("document_large_with_text_and_image.pdf"),
        }

    @pytest.mark.asyncio
    async def test_read_file(self, document_service, valid_document_data):
        """Test that extract_data_from_document reads a file successfully."""
        tenant_id = valid_document_data["tenant_id"]
        document_path = valid_document_data["document_path"]
        document = await document_service.extract_data_from_document(tenant_id, document_path)
        assert document.tenant_id == tenant_id
        assert document.name == os.path.basename(document_path)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "missing_file,empty_tenant",
        [
            (True, False),  # Missing file
            (False, True),  # Empty tenant ID
        ],
    )
    async def test_validation_errors(self, document_service, missing_file, empty_tenant):
        """Test validation errors in extract_data_from_document."""
        tenant_id = "" if empty_tenant else "test-tenant"
        document_path = "/non/existent/path.pdf" if missing_file else self.get_test_file_path("document.pdf")
        with patch("os.path.exists", return_value=not missing_file):
            if missing_file:
                with pytest.raises(FileNotFoundException):
                    await document_service.extract_data_from_document(tenant_id, document_path)
            elif empty_tenant:
                with pytest.raises(ValueError, match="Tenant ID is required"):
                    await document_service.extract_data_from_document(tenant_id, document_path)


class TestEmbeddingService:
    """Test suite for the EmbeddingService."""

    @pytest.fixture
    def mock_embedding_model(self):
        """Return a mock EmbeddingModel for testing."""
        model = Mock(spec=EmbeddingModel)
        model.model_name = "test-embedding-model"
        # Mock de embeddings para 3 chunks
        model.generate_texts_embeddings = AsyncMock(
            return_value=[
                [0.1, 0.2, 0.3],  # Embedding para o primeiro chunk
                [0.4, 0.5, 0.6],  # Embedding para o segundo chunk
                [0.7, 0.8, 0.9],  # Embedding para o terceiro chunk
            ]
        )
        return model

    @pytest.fixture
    def mock_repository(self):
        """Return a mock repository for testing."""
        repository = Mock(spec=BaseRepository)

        # Cria um documento de teste
        document_id = uuid.uuid4()
        document = Document(
            id=document_id, tenant_id="test-tenant", name="test-document.pdf", status=DocumentStatusEnum.uploaded
        )
        repository.get_document = AsyncMock(return_value=document)

        # Cria 3 chunks para o documento
        chunks = [
            Chunk(
                id=uuid.uuid4(),
                tenant_id="test-tenant",
                document_id=document_id,
                type=ChunkTypeEnum.paragraph,
                chunk="Este é o primeiro chunk",
                page_number=1,
            ),
            Chunk(
                id=uuid.uuid4(),
                tenant_id="test-tenant",
                document_id=document_id,
                type=ChunkTypeEnum.paragraph,
                chunk="Este é o segundo chunk",
                page_number=1,
            ),
            Chunk(
                id=uuid.uuid4(),
                tenant_id="test-tenant",
                document_id=document_id,
                type=ChunkTypeEnum.paragraph,
                chunk="Este é o terceiro chunk",
                page_number=2,
            ),
        ]
        repository.get_document_chunks = Mock(return_value=chunks)
        repository.update_document = AsyncMock()
        repository.update_chunks = AsyncMock()

        return repository

    @pytest.fixture
    def embedding_service(self, mock_embedding_model, mock_repository):
        """Return an EmbeddingDocumentService instance for testing."""
        return EmbeddingDocumentService(
            embedding_model=mock_embedding_model,
            repository=mock_repository,
            batch_size=10,  # Batch size pequeno para testes
        )

    @pytest.mark.asyncio
    async def test_process_document_generates_embeddings(
        self, embedding_service, mock_repository, mock_embedding_model
    ):
        """Testa se process_document gera embeddings corretamente para todos os chunks."""
        # Prepara os dados para o teste
        document_id = mock_repository.get_document.return_value.id
        tenant_id = "test-tenant"

        # Executa o processamento do documento
        await embedding_service.process_document(tenant_id, document_id)

        # Verifica se o status do documento foi atualizado para PROCESSING
        mock_repository.get_document.assert_called_once_with(tenant_id, document_id)
        assert mock_repository.update_document.called

        # Verifica se os embeddings foram gerados
        mock_embedding_model.generate_texts_embeddings.assert_called_once()

        # Verifica se os chunks foram atualizados com os embeddings
        assert mock_repository.update_chunks.called

        # Obtém os chunks atualizados passados para update_chunks
        updated_chunks = mock_repository.update_chunks.call_args[0][0]

        # Verifica se todos os 3 chunks receberam embeddings
        assert len(updated_chunks) == 3

        # Verifica os valores específicos dos embeddings para cada chunk
        assert updated_chunks[0].embedding == [0.1, 0.2, 0.3]
        assert updated_chunks[1].embedding == [0.4, 0.5, 0.6]
        assert updated_chunks[2].embedding == [0.7, 0.8, 0.9]
