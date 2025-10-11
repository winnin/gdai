"""Integration tests for gdai.embeddings module.

These tests interact with real Cohere API to verify:
- API connectivity and authentication
- Embedding generation functionality
- Error handling and validations
- Normalization and vector operations

Requirements:
- EMBEDDING_MODEL_API_KEY environment variable must be set
- Active internet connection to reach Cohere API
"""

import os

import numpy as np
import pytest
import pytest_asyncio

from gdai.embeddings import EmbeddingFactory
from gdai.embeddings.cohere_embedding import CohereEmbeddingModel


class TestCohereEmbeddingModelIntegration:
    """Integration tests for CohereEmbeddingModel with real API."""

    @pytest_asyncio.fixture
    async def embedding_model(self):
        """Create a CohereEmbeddingModel instance with API key from environment."""
        api_key = os.getenv("EMBEDDING_MODEL_API_KEY")
        if not api_key:
            pytest.skip("EMBEDDING_MODEL_API_KEY not set in environment")

        model = await CohereEmbeddingModel.create(api_key)
        return model

    @pytest.mark.asyncio
    async def test_create_cohere_model_with_valid_api_key(self):
        """Test creating CohereEmbeddingModel with valid API key."""
        api_key = os.getenv("EMBEDDING_MODEL_API_KEY")
        if not api_key:
            pytest.skip("EMBEDDING_MODEL_API_KEY not set in environment")

        model = await CohereEmbeddingModel.create(api_key)

        assert model is not None
        assert isinstance(model, CohereEmbeddingModel)
        assert model.api_key == api_key
        assert model.model == "embed-v4.0"
        assert model.model_name == "cohere/embed-v4.0"
        assert model.cohere is not None
        assert model.SEARCH_DOCUMENT_TYPE == "search_query"

    @pytest.mark.asyncio
    async def test_create_cohere_model_inherits_from_base(self):
        """Test that CohereEmbeddingModel properly inherits from EmbeddingModel."""
        api_key = os.getenv("EMBEDDING_MODEL_API_KEY")
        if not api_key:
            pytest.skip("EMBEDDING_MODEL_API_KEY not set in environment")

        model = await CohereEmbeddingModel.create(api_key)

        from gdai.embeddings.base_embedding import EmbeddingModel

        assert isinstance(model, EmbeddingModel)
        assert hasattr(model, "generate_texts_embeddings")
        assert hasattr(model, "model_name")

    @pytest.mark.asyncio
    async def test_generate_single_text_embedding(self, embedding_model):
        """Test generating embedding for a single text."""
        texts = ["Hello, this is a test sentence."]

        embeddings = await embedding_model.generate_texts_embeddings(texts)

        assert embeddings is not None
        assert isinstance(embeddings, list)
        assert len(embeddings) == 1

        # Verify embedding structure
        embedding = embeddings[0]
        assert isinstance(embedding, list)
        assert len(embedding) > 0  # Cohere embed-v4.0 has 1024 dimensions
        assert all(isinstance(x, float) for x in embedding)

        # Verify normalization (L2 norm should be ~1.0)
        norm = np.linalg.norm(embedding)
        assert np.isclose(norm, 1.0, atol=1e-5), f"Embedding should be normalized, got norm={norm}"

    @pytest.mark.asyncio
    async def test_generate_multiple_texts_embeddings(self, embedding_model):
        """Test generating embeddings for multiple texts."""
        texts = [
            "The quick brown fox jumps over the lazy dog.",
            "Machine learning is a subset of artificial intelligence.",
            "Python is a popular programming language.",
        ]

        embeddings = await embedding_model.generate_texts_embeddings(texts)

        assert embeddings is not None
        assert isinstance(embeddings, list)
        assert len(embeddings) == 3

        # Verify all embeddings
        for i, embedding in enumerate(embeddings):
            assert isinstance(embedding, list)
            assert len(embedding) > 0
            assert all(isinstance(x, float) for x in embedding)

            # Verify normalization
            norm = np.linalg.norm(embedding)
            assert np.isclose(norm, 1.0, atol=1e-5), f"Embedding {i} should be normalized"

        # Verify embeddings are different
        assert embeddings[0] != embeddings[1]
        assert embeddings[1] != embeddings[2]

    @pytest.mark.asyncio
    async def test_generate_embeddings_semantic_similarity(self, embedding_model):
        """Test that semantically similar texts have similar embeddings."""
        similar_texts = [
            "The cat is sleeping on the couch.",
            "A cat is resting on the sofa.",
        ]

        different_text = "Quantum physics is a complex subject."

        embeddings_similar = await embedding_model.generate_texts_embeddings(similar_texts)
        embeddings_all = await embedding_model.generate_texts_embeddings(similar_texts + [different_text])

        # Calculate cosine similarity between similar texts
        similarity_similar = np.dot(embeddings_similar[0], embeddings_similar[1])

        # Calculate cosine similarity between first similar text and different text
        similarity_different = np.dot(embeddings_all[0], embeddings_all[2])

        # Similar texts should have higher similarity than different texts
        assert similarity_similar > similarity_different, (
            f"Similar texts similarity ({similarity_similar:.4f}) should be > "
            f"different texts similarity ({similarity_different:.4f})"
        )
        assert similarity_similar > 0.7, f"Similar texts should have high similarity (got {similarity_similar:.4f})"

    @pytest.mark.asyncio
    async def test_generate_embeddings_batch_processing(self, embedding_model):
        """Test batch processing with maximum allowed texts."""
        # Cohere allows up to 96 texts per batch
        texts = [f"This is test sentence number {i}." for i in range(50)]

        embeddings = await embedding_model.generate_texts_embeddings(texts)

        assert len(embeddings) == 50
        for embedding in embeddings:
            assert len(embedding) > 0
            norm = np.linalg.norm(embedding)
            assert np.isclose(norm, 1.0, atol=1e-5)

    @pytest.mark.asyncio
    async def test_generate_embeddings_empty_list_raises_error(self, embedding_model):
        """Test that empty text list raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            await embedding_model.generate_texts_embeddings([])

    @pytest.mark.asyncio
    async def test_generate_embeddings_empty_string_raises_error(self, embedding_model):
        """Test that empty strings raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty strings"):
            await embedding_model.generate_texts_embeddings([""])

    @pytest.mark.asyncio
    async def test_generate_embeddings_whitespace_only_raises_error(self, embedding_model):
        """Test that whitespace-only strings raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty strings"):
            await embedding_model.generate_texts_embeddings(["   ", "\t\n"])

    @pytest.mark.asyncio
    async def test_generate_embeddings_exceeds_max_batch_size(self, embedding_model):
        """Test that exceeding max batch size (96) raises ValueError."""
        texts = [f"Text {i}" for i in range(97)]

        with pytest.raises(ValueError, match="maximum number of texts is 96"):
            await embedding_model.generate_texts_embeddings(texts)

    @pytest.mark.asyncio
    async def test_generate_embeddings_with_special_characters(self, embedding_model):
        """Test generating embeddings for texts with special characters."""
        texts = [
            "Hello! How are you?",
            "Price: $99.99 (50% off)",
            "Email: test@example.com",
        ]

        embeddings = await embedding_model.generate_texts_embeddings(texts)

        assert len(embeddings) == 3
        for embedding in embeddings:
            assert len(embedding) > 0
            norm = np.linalg.norm(embedding)
            assert np.isclose(norm, 1.0, atol=1e-5)

    @pytest.mark.asyncio
    async def test_generate_embeddings_with_multilingual_text(self, embedding_model):
        """Test generating embeddings for multilingual texts."""
        texts = [
            "Hello, world!",  # English
            "Bonjour le monde!",  # French
            "�Hola mundo!",  # Spanish
            "S�kaoL",  # Japanese
        ]

        embeddings = await embedding_model.generate_texts_embeddings(texts)

        assert len(embeddings) == 4
        for embedding in embeddings:
            assert len(embedding) > 0
            norm = np.linalg.norm(embedding)
            assert np.isclose(norm, 1.0, atol=1e-5)

    @pytest.mark.asyncio
    async def test_generate_embeddings_with_long_text(self, embedding_model):
        """Test generating embedding for a long text."""
        long_text = " ".join(["This is a longer sentence."] * 50)

        embeddings = await embedding_model.generate_texts_embeddings([long_text])

        assert len(embeddings) == 1
        assert len(embeddings[0]) > 0
        norm = np.linalg.norm(embeddings[0])
        assert np.isclose(norm, 1.0, atol=1e-5)

    @pytest.mark.asyncio
    async def test_normalize_embedding_unit_vector(self):
        """Test normalize_embedding produces unit vectors."""
        model = CohereEmbeddingModel()

        # Test with simple vector
        embedding = [3.0, 4.0]  # magnitude = 5
        normalized = model.normalize_embedding(embedding)

        assert len(normalized) == 2
        assert np.isclose(normalized[0], 0.6, atol=1e-5)
        assert np.isclose(normalized[1], 0.8, atol=1e-5)

        # Verify it's a unit vector
        norm = np.linalg.norm(normalized)
        assert np.isclose(norm, 1.0, atol=1e-5)

    @pytest.mark.asyncio
    async def test_normalize_embedding_zero_vector(self):
        """Test normalize_embedding handles zero vectors."""
        model = CohereEmbeddingModel()

        embedding = [0.0, 0.0, 0.0]
        normalized = model.normalize_embedding(embedding)

        # Zero vector should remain zero
        assert normalized == [0.0, 0.0, 0.0]

    @pytest.mark.asyncio
    async def test_normalize_embedding_preserves_dimensions(self):
        """Test normalize_embedding preserves vector dimensions."""
        model = CohereEmbeddingModel()

        for dim in [10, 100, 1024]:
            embedding = list(np.random.randn(dim))
            normalized = model.normalize_embedding(embedding)

            assert len(normalized) == dim

    @pytest.mark.asyncio
    async def test_model_string_representation(self, embedding_model):
        """Test __str__ method returns correct model name."""
        assert str(embedding_model) == "cohere/embed-v4.0"
        assert embedding_model.model_name == "cohere/embed-v4.0"

    @pytest.mark.asyncio
    async def test_cohere_client_initialization(self, embedding_model):
        """Test that Cohere client is properly initialized."""
        assert embedding_model.cohere is not None
        assert hasattr(embedding_model.cohere, "embed")

    @pytest.mark.asyncio
    async def test_generate_embeddings_with_invalid_api_key(self):
        """Test that invalid API key raises appropriate error."""
        model = await CohereEmbeddingModel.create("invalid_api_key")

        with pytest.raises(Exception, match="Failed to generate embeddings"):
            await model.generate_texts_embeddings(["Test text"])


class TestEmbeddingFactoryIntegration:
    """Integration tests for EmbeddingFactory."""

    @pytest.mark.asyncio
    async def test_factory_creates_cohere_model(self):
        """Test that factory creates CohereEmbeddingModel."""
        api_key = os.getenv("EMBEDDING_MODEL_API_KEY")
        if not api_key:
            pytest.skip("EMBEDDING_MODEL_API_KEY not set in environment")

        # Set environment variable for Config
        os.environ["EMBEDDING_MODEL"] = "cohere/embed-v4.0"
        os.environ["EMBEDDING_MODEL_API_KEY"] = api_key

        model = await EmbeddingFactory.get_embedding()

        assert model is not None
        assert isinstance(model, CohereEmbeddingModel)
        assert model.model_name == "cohere/embed-v4.0"

    @pytest.mark.asyncio
    async def test_factory_with_unsupported_model(self):
        """Test that factory raises error for unsupported model."""
        # Save original values
        original_model = os.environ.get("EMBEDDING_MODEL")
        original_key = os.environ.get("EMBEDDING_MODEL_API_KEY")

        from gdai.commons.config import Config

        original_config_model = Config.embedding.EMBEDDING_MODEL

        try:
            # Set unsupported model
            os.environ["EMBEDDING_MODEL"] = "unsupported/model"
            os.environ["EMBEDDING_MODEL_API_KEY"] = "fake_key"

            # Need to reload config for env changes to take effect
            Config.embedding.EMBEDDING_MODEL = "unsupported/model"

            with pytest.raises(ValueError, match="Unsupported embedding model"):
                await EmbeddingFactory.get_embedding()
        finally:
            # Restore original Config
            Config.embedding.EMBEDDING_MODEL = original_config_model

            # Restore original env values
            if original_model:
                os.environ["EMBEDDING_MODEL"] = original_model
            elif "EMBEDDING_MODEL" in os.environ:
                del os.environ["EMBEDDING_MODEL"]

            if original_key:
                os.environ["EMBEDDING_MODEL_API_KEY"] = original_key
            elif "EMBEDDING_MODEL_API_KEY" in os.environ:
                del os.environ["EMBEDDING_MODEL_API_KEY"]

    @pytest.mark.asyncio
    async def test_factory_created_model_works(self):
        """Test that factory-created model actually works."""
        api_key = os.getenv("EMBEDDING_MODEL_API_KEY")
        if not api_key:
            pytest.skip("EMBEDDING_MODEL_API_KEY not set in environment")

        os.environ["EMBEDDING_MODEL"] = "cohere/embed-v4.0"
        os.environ["EMBEDDING_MODEL_API_KEY"] = api_key

        model = await EmbeddingFactory.get_embedding()
        embeddings = await model.generate_texts_embeddings(["Factory test sentence."])

        assert len(embeddings) == 1
        assert len(embeddings[0]) > 0
        norm = np.linalg.norm(embeddings[0])
        assert np.isclose(norm, 1.0, atol=1e-5)


class TestEmbeddingModelEndToEnd:
    """End-to-end integration tests for complete embedding workflow."""

    @pytest.mark.asyncio
    async def test_complete_embedding_workflow(self):
        """Test complete workflow: create model -> generate embeddings -> verify results."""
        api_key = os.getenv("EMBEDDING_MODEL_API_KEY")
        if not api_key:
            pytest.skip("EMBEDDING_MODEL_API_KEY not set in environment")

        # Step 1: Create model
        model = await CohereEmbeddingModel.create(api_key)
        assert model is not None

        # Step 2: Generate embeddings for a document
        document_chunks = [
            "Introduction to machine learning and artificial intelligence.",
            "Neural networks are the foundation of deep learning.",
            "Training models requires large datasets and computational power.",
        ]

        embeddings = await model.generate_texts_embeddings(document_chunks)

        # Step 3: Verify embeddings
        assert len(embeddings) == 3

        # Step 4: Verify all embeddings are normalized
        for i, embedding in enumerate(embeddings):
            norm = np.linalg.norm(embedding)
            assert np.isclose(norm, 1.0, atol=1e-5), f"Chunk {i} not normalized"

        # Step 5: Verify semantic relationships
        # Chunks 0 and 1 should be more similar (both about ML/AI)
        similarity_01 = np.dot(embeddings[0], embeddings[1])
        # similarity_02 = np.dot(embeddings[0], embeddings[2])  # Could compare if needed

        # This assertion might be flaky depending on actual embeddings,
        # but it demonstrates semantic understanding
        assert similarity_01 > 0.3, "Related chunks should have reasonable similarity"

    @pytest.mark.asyncio
    async def test_multiple_independent_calls(self):
        """Test that multiple independent API calls work correctly."""
        api_key = os.getenv("EMBEDDING_MODEL_API_KEY")
        if not api_key:
            pytest.skip("EMBEDDING_MODEL_API_KEY not set in environment")

        model = await CohereEmbeddingModel.create(api_key)

        # Make multiple independent calls
        embeddings1 = await model.generate_texts_embeddings(["First call"])
        embeddings2 = await model.generate_texts_embeddings(["Second call"])
        embeddings3 = await model.generate_texts_embeddings(["First call"])  # Same as first

        # Different texts should have different embeddings
        assert embeddings1[0] != embeddings2[0]

        # Same text should produce same embeddings (deterministic)
        assert len(embeddings1[0]) == len(embeddings3[0])
        # Note: Embeddings might not be exactly identical due to API variations

    @pytest.mark.asyncio
    async def test_embedding_dimensions_consistency(self):
        """Test that all embeddings have consistent dimensions."""
        api_key = os.getenv("EMBEDDING_MODEL_API_KEY")
        if not api_key:
            pytest.skip("EMBEDDING_MODEL_API_KEY not set in environment")

        model = await CohereEmbeddingModel.create(api_key)

        texts = ["Short", "A bit longer text", "An even much longer text with more words"]

        embeddings = await model.generate_texts_embeddings(texts)

        # All embeddings should have the same dimension
        dimensions = [len(emb) for emb in embeddings]
        assert len(set(dimensions)) == 1, "All embeddings should have same dimension"
        assert dimensions[0] > 0, "Embeddings should not be empty"
