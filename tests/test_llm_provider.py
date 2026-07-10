import pytest
import os
from unittest.mock import patch, MagicMock
from core.llm_provider import LLMProviderFactory, LLMProvider, OpenAIProvider, GeminiProvider

def test_get_llm_provider_unknown():
    with patch('core.llm_config.LLMConfigManager.get_active_provider', return_value='unknown_provider'):
        with pytest.raises(ValueError, match="Unknown LLM provider: unknown_provider"):
            LLMProviderFactory.create()

def test_get_llm_provider_no_config():
    with patch('core.llm_config.LLMConfigManager.get_active_provider', return_value=None):
        with pytest.raises(ValueError, match="No LLM provider selected."):
            LLMProviderFactory.create()

@patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}, clear=True)
def test_openai_provider_graceful_fail_no_sdk():
    # If openai is not installed, it should raise ImportError
    with patch.dict('sys.modules', {'openai': None}):
        with pytest.raises(ImportError, match="Missing required dependency. Please run: pip install openai"):
            LLMProviderFactory.create('openai')

@patch.dict(os.environ, {}, clear=True)
def test_openai_provider_missing_key():
    # Mock openai SDK being present
    with patch.dict('sys.modules', {'openai': MagicMock()}):
        with pytest.raises(ValueError, match="OPENAI_API_KEY missing from environment"):
            LLMProviderFactory.create('openai')

def test_provider_raw_flags():
    with patch.dict('sys.modules', {'openai': MagicMock()}):
        with patch('core.llm_config.LLMConfigManager.get_api_key', return_value='test_key'):
            provider = LLMProviderFactory.create('openai', raw_send=True, raw_return=True)
            assert provider.raw_send is True
            assert provider.raw_return is True
