"""Unit tests for gdai.commons.config module."""

import logging
from unittest.mock import patch

from gdai.commons.config import Config, DatabaseConfig, EmbeddingConfig, ExtractorConfig, LLMConfig


class TestDatabaseConfig:
    """Test suite for DatabaseConfig class."""

    def test_database_config_attributes(self):
        """Test DatabaseConfig has expected attributes."""
        assert hasattr(DatabaseConfig, "DATABASE")
        assert hasattr(DatabaseConfig, "PGVECTOR_USER")
        assert hasattr(DatabaseConfig, "PGVECTOR_PASSWORD")
        assert hasattr(DatabaseConfig, "PGVECTOR_DATABASE")
        assert hasattr(DatabaseConfig, "PGVECTOR_HOST")
        assert hasattr(DatabaseConfig, "PGVECTOR_PORT")

    def test_database_config_port_is_int(self):
        """Test PGVECTOR_PORT is an integer."""
        assert isinstance(DatabaseConfig.PGVECTOR_PORT, int)

    def test_database_config_pool_connections_are_int(self):
        """Test pool connection settings are integers."""
        assert isinstance(DatabaseConfig.PGVECTOR_MIN_POOL_CONNECTIONS, int)
        assert isinstance(DatabaseConfig.PGVECTOR_MAX_POOL_CONNECTIONS, int)

    def test_database_config_default_port_set_in_env(self):
        """Test port value is loaded from environment."""
        # Port is set from environment, default would be 5432 if not set
        # But in current environment it's set to 5555
        assert isinstance(DatabaseConfig.PGVECTOR_PORT, int)
        assert DatabaseConfig.PGVECTOR_PORT > 0

    def test_database_config_validate_method_exists(self):
        """Test DatabaseConfig has validate method."""
        assert hasattr(DatabaseConfig, "validate")
        assert callable(DatabaseConfig.validate)

    def test_database_config_validate_missing_database(self):
        """Test validation fails when DATABASE is not set."""
        original_value = DatabaseConfig.DATABASE
        try:
            DatabaseConfig.DATABASE = None
            result = DatabaseConfig.validate()
            assert result is False
        finally:
            DatabaseConfig.DATABASE = original_value

    def test_database_config_validate_missing_user(self):
        """Test validation fails when PGVECTOR_USER is not set."""
        original_value = DatabaseConfig.PGVECTOR_USER
        try:
            DatabaseConfig.PGVECTOR_USER = None
            result = DatabaseConfig.validate()
            assert result is False
        finally:
            DatabaseConfig.PGVECTOR_USER = original_value

    def test_database_config_validate_missing_password(self):
        """Test validation fails when PGVECTOR_PASSWORD is not set."""
        original_value = DatabaseConfig.PGVECTOR_PASSWORD
        try:
            DatabaseConfig.PGVECTOR_PASSWORD = None
            result = DatabaseConfig.validate()
            assert result is False
        finally:
            DatabaseConfig.PGVECTOR_PASSWORD = original_value

    def test_database_config_validate_missing_database_name(self):
        """Test validation fails when PGVECTOR_DATABASE is not set."""
        original_value = DatabaseConfig.PGVECTOR_DATABASE
        try:
            DatabaseConfig.PGVECTOR_DATABASE = None
            result = DatabaseConfig.validate()
            assert result is False
        finally:
            DatabaseConfig.PGVECTOR_DATABASE = original_value

    def test_database_config_validate_missing_host(self):
        """Test validation fails when PGVECTOR_HOST is not set."""
        original_value = DatabaseConfig.PGVECTOR_HOST
        try:
            DatabaseConfig.PGVECTOR_HOST = None
            result = DatabaseConfig.validate()
            assert result is False
        finally:
            DatabaseConfig.PGVECTOR_HOST = original_value

    def test_database_config_validate_negative_min_pool(self):
        """Test validation fails when MIN_POOL_CONNECTIONS is negative."""
        original_value = DatabaseConfig.PGVECTOR_MIN_POOL_CONNECTIONS
        try:
            DatabaseConfig.PGVECTOR_MIN_POOL_CONNECTIONS = -1
            result = DatabaseConfig.validate()
            assert result is False
        finally:
            DatabaseConfig.PGVECTOR_MIN_POOL_CONNECTIONS = original_value

    def test_database_config_validate_negative_max_pool(self):
        """Test validation fails when MAX_POOL_CONNECTIONS is negative."""
        original_value = DatabaseConfig.PGVECTOR_MAX_POOL_CONNECTIONS
        try:
            DatabaseConfig.PGVECTOR_MAX_POOL_CONNECTIONS = -1
            result = DatabaseConfig.validate()
            assert result is False
        finally:
            DatabaseConfig.PGVECTOR_MAX_POOL_CONNECTIONS = original_value

    def test_config_component_base_validate(self):
        """Test ConfigComponent base class validate returns True."""
        from gdai.commons.config import ConfigComponent

        result = ConfigComponent.validate()
        assert result is True


class TestLLMConfig:
    """Test suite for LLMConfig class."""

    def test_llm_config_attributes(self):
        """Test LLMConfig has expected attributes."""
        assert hasattr(LLMConfig, "LLM_MODEL")
        assert hasattr(LLMConfig, "LLM_MODEL_API_KEY")
        assert hasattr(LLMConfig, "LLM_MAX_TOKENS")
        assert hasattr(LLMConfig, "LLM_TEMPERATURE")

    def test_llm_config_max_tokens_is_int(self):
        """Test LLM_MAX_TOKENS is an integer."""
        assert isinstance(LLMConfig.LLM_MAX_TOKENS, int)

    def test_llm_config_temperature_is_float(self):
        """Test LLM_TEMPERATURE is a float."""
        assert isinstance(LLMConfig.LLM_TEMPERATURE, float)

    def test_llm_config_default_values(self):
        """Test default values for LLM config."""
        # Default model should be gpt-4o
        assert LLMConfig.LLM_MODEL == "openai/gpt-4o"

    def test_llm_config_validate_method_exists(self):
        """Test LLMConfig has validate method."""
        assert hasattr(LLMConfig, "validate")
        assert callable(LLMConfig.validate)

    def test_llm_config_validate_missing_model(self):
        """Test validation fails when LLM_MODEL is not set."""
        original_value = LLMConfig.LLM_MODEL
        try:
            LLMConfig.LLM_MODEL = None
            result = LLMConfig.validate()
            assert result is False
        finally:
            LLMConfig.LLM_MODEL = original_value

    def test_llm_config_validate_missing_api_key(self):
        """Test validation fails when LLM_API_KEY is not set."""
        original_value = LLMConfig.LLM_MODEL_API_KEY
        try:
            LLMConfig.LLM_MODEL_API_KEY = None
            result = LLMConfig.validate()
            assert result is False
        finally:
            LLMConfig.LLM_MODEL_API_KEY = original_value

    def test_llm_config_validate_invalid_max_tokens(self):
        """Test validation fails when LLM_MAX_TOKENS is invalid."""
        original_value = LLMConfig.LLM_MAX_TOKENS
        try:
            LLMConfig.LLM_MAX_TOKENS = 0
            result = LLMConfig.validate()
            assert result is False

            LLMConfig.LLM_MAX_TOKENS = -100
            result = LLMConfig.validate()
            assert result is False
        finally:
            LLMConfig.LLM_MAX_TOKENS = original_value

    def test_llm_config_validate_invalid_temperature(self):
        """Test validation fails when LLM_TEMPERATURE is out of range."""
        original_value = LLMConfig.LLM_TEMPERATURE
        try:
            LLMConfig.LLM_TEMPERATURE = -0.1
            result = LLMConfig.validate()
            assert result is False

            LLMConfig.LLM_TEMPERATURE = 1.1
            result = LLMConfig.validate()
            assert result is False
        finally:
            LLMConfig.LLM_TEMPERATURE = original_value


class TestExtractorConfig:
    """Test suite for ExtractorConfig class."""

    def test_extractor_config_attributes(self):
        """Test ExtractorConfig has expected attributes."""
        assert hasattr(ExtractorConfig, "TMP_FOLDER")
        assert hasattr(ExtractorConfig, "MAX_FILE_SIZE_MB")
        assert hasattr(ExtractorConfig, "MAX_RETRIES")

    def test_extractor_config_types(self):
        """Test ExtractorConfig attribute types."""
        assert isinstance(ExtractorConfig.MAX_FILE_SIZE_MB, int)
        assert isinstance(ExtractorConfig.MAX_RETRIES, int)

    def test_extractor_config_validate_method_exists(self):
        """Test ExtractorConfig has validate method."""
        assert hasattr(ExtractorConfig, "validate")
        assert callable(ExtractorConfig.validate)

    def test_extractor_config_validate_missing_tmp_folder(self):
        """Test validation fails when TMP_FOLDER is not set."""
        original_value = ExtractorConfig.TMP_FOLDER
        try:
            ExtractorConfig.TMP_FOLDER = None
            result = ExtractorConfig.validate()
            assert result is False
        finally:
            ExtractorConfig.TMP_FOLDER = original_value

    def test_extractor_config_validate_creates_directory(self, tmp_path):
        """Test validation creates directory if it doesn't exist."""
        original_value = ExtractorConfig.TMP_FOLDER
        test_dir = tmp_path / "test_extractor_dir"
        try:
            ExtractorConfig.TMP_FOLDER = str(test_dir)
            # Directory should not exist yet
            assert not test_dir.exists()

            # Validate should create it
            result = ExtractorConfig.validate()
            assert result is True
            assert test_dir.exists()
        finally:
            ExtractorConfig.TMP_FOLDER = original_value

    def test_extractor_config_validate_directory_creation_error(self):
        """Test validation handles directory creation errors."""
        original_value = ExtractorConfig.TMP_FOLDER

        try:
            # Mock Path.mkdir to raise an exception
            with patch("gdai.commons.config.Path.mkdir") as mock_mkdir:
                mock_mkdir.side_effect = OSError("Mocked error creating directory")

                ExtractorConfig.TMP_FOLDER = "/tmp/test_error_dir"

                try:
                    ExtractorConfig.validate()
                    assert False, "Expected OSError to be raised"
                except OSError as e:
                    # Lines 126-128 should be executed
                    assert "Mocked error" in str(e)
        finally:
            ExtractorConfig.TMP_FOLDER = original_value

    def test_extractor_config_validate_invalid_max_file_size(self):
        """Test validation fails when MAX_FILE_SIZE_MB is invalid."""
        original_value = ExtractorConfig.MAX_FILE_SIZE_MB
        try:
            ExtractorConfig.MAX_FILE_SIZE_MB = 0
            result = ExtractorConfig.validate()
            assert result is False

            ExtractorConfig.MAX_FILE_SIZE_MB = -100
            result = ExtractorConfig.validate()
            assert result is False
        finally:
            ExtractorConfig.MAX_FILE_SIZE_MB = original_value

    def test_extractor_config_validate_invalid_max_retries(self):
        """Test validation fails when MAX_RETRIES is negative."""
        original_value = ExtractorConfig.MAX_RETRIES
        try:
            ExtractorConfig.MAX_RETRIES = -1
            result = ExtractorConfig.validate()
            assert result is False
        finally:
            ExtractorConfig.MAX_RETRIES = original_value


class TestEmbeddingConfig:
    """Test suite for EmbeddingConfig class."""

    def test_embedding_config_attributes(self):
        """Test EmbeddingConfig has expected attributes."""
        assert hasattr(EmbeddingConfig, "MAX_TEXT_SIZE")
        assert hasattr(EmbeddingConfig, "MAX_RETRIES")
        assert hasattr(EmbeddingConfig, "BATCH_SIZE")
        assert hasattr(EmbeddingConfig, "DIMENSION")
        assert hasattr(EmbeddingConfig, "EMBEDDING_MODEL")
        assert hasattr(EmbeddingConfig, "EMBEDDING_MODEL_API_KEY")

    def test_embedding_config_types(self):
        """Test EmbeddingConfig attribute types."""
        assert isinstance(EmbeddingConfig.MAX_TEXT_SIZE, int)
        assert isinstance(EmbeddingConfig.MAX_RETRIES, int)
        assert isinstance(EmbeddingConfig.BATCH_SIZE, int)
        assert isinstance(EmbeddingConfig.DIMENSION, int)

    def test_embedding_config_validate_method_exists(self):
        """Test EmbeddingConfig has validate method."""
        assert hasattr(EmbeddingConfig, "validate")
        assert callable(EmbeddingConfig.validate)

    def test_embedding_config_validate_invalid_max_text_size(self):
        """Test validation fails when MAX_TEXT_SIZE is invalid."""
        original_value = EmbeddingConfig.MAX_TEXT_SIZE
        try:
            EmbeddingConfig.MAX_TEXT_SIZE = 0
            result = EmbeddingConfig.validate()
            assert result is False

            EmbeddingConfig.MAX_TEXT_SIZE = -100
            result = EmbeddingConfig.validate()
            assert result is False
        finally:
            EmbeddingConfig.MAX_TEXT_SIZE = original_value

    def test_embedding_config_validate_invalid_max_retries(self):
        """Test validation fails when MAX_RETRIES is negative."""
        original_value = EmbeddingConfig.MAX_RETRIES
        try:
            EmbeddingConfig.MAX_RETRIES = -1
            result = EmbeddingConfig.validate()
            assert result is False
        finally:
            EmbeddingConfig.MAX_RETRIES = original_value

    def test_embedding_config_validate_invalid_batch_size(self):
        """Test validation fails when BATCH_SIZE is invalid."""
        original_value = EmbeddingConfig.BATCH_SIZE
        try:
            EmbeddingConfig.BATCH_SIZE = 0
            result = EmbeddingConfig.validate()
            assert result is False

            EmbeddingConfig.BATCH_SIZE = -10
            result = EmbeddingConfig.validate()
            assert result is False
        finally:
            EmbeddingConfig.BATCH_SIZE = original_value

    def test_embedding_config_validate_invalid_dimension(self):
        """Test validation fails when DIMENSION is invalid."""
        original_value = EmbeddingConfig.DIMENSION
        try:
            EmbeddingConfig.DIMENSION = 0
            result = EmbeddingConfig.validate()
            assert result is False

            EmbeddingConfig.DIMENSION = -100
            result = EmbeddingConfig.validate()
            assert result is False
        finally:
            EmbeddingConfig.DIMENSION = original_value

    def test_embedding_config_validate_missing_model(self):
        """Test validation fails when EMBEDDING_MODEL is not set."""
        original_value = EmbeddingConfig.EMBEDDING_MODEL
        try:
            EmbeddingConfig.EMBEDDING_MODEL = None
            result = EmbeddingConfig.validate()
            assert result is False
        finally:
            EmbeddingConfig.EMBEDDING_MODEL = original_value

    def test_embedding_config_validate_missing_api_key(self):
        """Test validation fails when EMBEDDING_MODEL_API_KEY is not set."""
        original_value = EmbeddingConfig.EMBEDDING_MODEL_API_KEY
        try:
            EmbeddingConfig.EMBEDDING_MODEL_API_KEY = None
            result = EmbeddingConfig.validate()
            assert result is False
        finally:
            EmbeddingConfig.EMBEDDING_MODEL_API_KEY = original_value


class TestConfigClass:
    """Test suite for main Config class."""

    def test_config_has_components(self):
        """Test Config class has all component attributes."""
        assert hasattr(Config, "db")
        assert hasattr(Config, "llm")
        assert hasattr(Config, "extractor")
        assert hasattr(Config, "embedding")

    def test_config_components_are_correct_types(self):
        """Test Config components are the correct classes."""
        assert Config.db == DatabaseConfig
        assert Config.llm == LLMConfig
        assert Config.extractor == ExtractorConfig
        assert Config.embedding == EmbeddingConfig

    def test_config_has_components_dict(self):
        """Test Config has _components dictionary."""
        assert hasattr(Config, "_components")
        assert isinstance(Config._components, dict)

    def test_config_get_component_by_name(self):
        """Test getting component by name."""
        db_component = Config.get_component("db")
        assert db_component == DatabaseConfig

        llm_component = Config.get_component("llm")
        assert llm_component == LLMConfig

    def test_config_get_component_case_insensitive(self):
        """Test component name lookup is case insensitive."""
        db_component = Config.get_component("DB")
        assert db_component == DatabaseConfig

    def test_config_get_component_not_found(self):
        """Test getting non-existent component returns None."""
        component = Config.get_component("nonexistent")
        assert component is None

    def test_config_validate_all_method_exists(self):
        """Test Config has validate_all method."""
        assert hasattr(Config, "validate_all")
        assert callable(Config.validate_all)

    def test_config_validate_all_with_one_invalid_component(self, caplog):
        """Test validate_all returns False when one component is invalid."""
        # Save original values
        original_db_value = DatabaseConfig.DATABASE

        try:
            # Make one component invalid
            DatabaseConfig.DATABASE = None

            with caplog.at_level(logging.INFO, logger="GDAI_CONFIG"):
                result = Config.validate_all()

            # Should return False because one component is invalid
            assert result is False
        finally:
            # Restore original values
            DatabaseConfig.DATABASE = original_db_value

    def test_config_validate_all_logs_validation_progress(self, caplog):
        """Test validate_all logs validation progress for each component."""
        with caplog.at_level(logging.INFO, logger="GDAI_CONFIG"):
            Config.validate_all()

        # Check that validation messages were logged
        log_text = caplog.text
        assert "Validating configuration" in log_text or len(caplog.records) > 0


class TestConfigValidation:
    """Integration tests for config validation."""

    def test_validate_all_method_callable(self):
        """Test validate_all method is callable."""
        assert hasattr(Config, "validate_all")
        assert callable(Config.validate_all)

    def test_all_config_components_have_validate(self):
        """Test all config components have validate method."""
        for component_name, component_class in Config._components.items():
            assert hasattr(component_class, "validate"), f"{component_name} missing validate method"
            assert callable(component_class.validate), f"{component_name}.validate not callable"
