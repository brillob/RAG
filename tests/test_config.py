"""Unit tests for configuration."""
import pytest
import os
from unittest.mock import patch
from app.config import Settings


def test_settings_defaults():
    """Test default settings values."""
    with patch.dict(os.environ, {}, clear=True):
        settings = Settings()
        
        assert settings.mode == "local"
        assert settings.chunking_strategy == "sentence"
        assert settings.enable_conversation_memory is True
        assert settings.max_conversation_history == 10
        assert settings.chunk_size == 500
        assert settings.chunk_overlap == 50


def test_is_local_mode():
    """Test local mode detection."""
    with patch.dict(os.environ, {"MODE": "local"}, clear=True):
        settings = Settings()
        assert settings.is_local_mode() is True
        assert settings.is_azure_mode() is False


def test_is_azure_mode():
    """Test Azure mode detection."""
    with patch.dict(os.environ, {"MODE": "azure"}, clear=True):
        settings = Settings()
        assert settings.is_azure_mode() is True
        assert settings.is_local_mode() is False


def test_settings_from_env():
    """Test loading settings from environment variables."""
    env_vars = {
        "MODE": "azure",
        "CHUNKING_STRATEGY": "semantic",
        "CHUNK_SIZE": "800",
        "CHUNK_OVERLAP": "100",
        "ENABLE_CONVERSATION_MEMORY": "false",
        "MAX_CONVERSATION_HISTORY": "5",
        "LOG_LEVEL": "DEBUG"
    }
    
    with patch.dict(os.environ, env_vars, clear=True):
        settings = Settings()
        
        assert settings.mode == "azure"
        assert settings.chunking_strategy == "semantic"
        assert settings.chunk_size == 800
        assert settings.chunk_overlap == 100
        assert settings.enable_conversation_memory is False
        assert settings.max_conversation_history == 5
        assert settings.log_level == "DEBUG"


def test_settings_case_insensitive():
    """Test that settings are case-insensitive."""
    with patch.dict(os.environ, {"MODE": "LOCAL", "LOG_LEVEL": "debug"}, clear=True):
        settings = Settings()
        
        assert settings.mode == "LOCAL"
        assert settings.log_level == "debug"


def test_settings_optional_azure_fields():
    """Test that Azure fields are optional in local mode."""
    with patch.dict(os.environ, {"MODE": "local"}, clear=True):
        settings = Settings()
        
        # Should not raise error even without Azure credentials
        assert settings.azure_search_endpoint is None or isinstance(settings.azure_search_endpoint, str)
        assert settings.azure_openai_endpoint is None or isinstance(settings.azure_openai_endpoint, str)
