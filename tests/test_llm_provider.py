import pytest
import os
import time
from unittest.mock import patch, MagicMock
from core.llm_provider import get_llm_provider, retry_with_backoff

def test_get_llm_provider_unknown():
    with patch('core.llm_config.LLMConfigManager.get_active_provider', return_value='unknown_provider'):
        with pytest.raises(ValueError, match="Unknown LLM provider: unknown_provider"):
            get_llm_provider()

def test_get_llm_provider_no_config():
    with patch('core.llm_config.LLMConfigManager.get_active_provider', return_value=None):
        with pytest.raises(ValueError, match="No LLM provider selected."):
            get_llm_provider()

@patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}, clear=True)
def test_openai_provider_graceful_fail_no_sdk():
    # If openai is not installed, it should raise ImportError
    with patch.dict('sys.modules', {'openai': None}):
        with pytest.raises(ImportError, match="Missing required dependency. Please run: pip install openai"):
            get_llm_provider('openai')

@patch.dict(os.environ, {}, clear=True)
def test_openai_provider_missing_key():
    # Mock openai SDK being present
    with patch.dict('sys.modules', {'openai': MagicMock()}):
        with pytest.raises(ValueError, match="OPENAI_API_KEY missing from environment"):
            get_llm_provider('openai')

def test_provider_raw_flags():
    with patch.dict('sys.modules', {'openai': MagicMock()}):
        with patch('core.llm_config.LLMConfigManager.get_api_key', return_value='test_key'):
            provider = get_llm_provider('openai', raw_send=True, raw_return=True)
            assert provider.raw_send is True
            assert provider.raw_return is True

def test_retry_success_immediately():
    mock_func = MagicMock(return_value="success")

    @retry_with_backoff(max_retries=3, base_delay=0.1)
    def decorated_func():
        return mock_func()

    result = decorated_func()
    assert result == "success"
    assert mock_func.call_count == 1

def test_retry_eventual_success():
    # Fail twice, then succeed
    mock_func = MagicMock(side_effect=[Exception("429 Too Many Requests"), Exception("rate limit exceeded"), "success"])

    @retry_with_backoff(max_retries=3, base_delay=0.1)
    def decorated_func():
        return mock_func()

    with patch("time.sleep") as mock_sleep:
        result = decorated_func()
        assert result == "success"
        assert mock_func.call_count == 3
        # Check delays: 0.1 * (2^0) = 0.1, 0.1 * (2^1) = 0.2
        mock_sleep.assert_any_call(0.1)
        mock_sleep.assert_any_call(0.2)
        assert mock_sleep.call_count == 2

def test_retry_max_retries_exceeded():
    # Always fail with retryable error
    mock_func = MagicMock(side_effect=Exception("429 error"))

    @retry_with_backoff(max_retries=2, base_delay=0.1)
    def decorated_func():
        return mock_func()

    with patch("time.sleep") as mock_sleep:
        with pytest.raises(Exception, match="429 error"):
            decorated_func()

        # Initial try + 2 retries = 3 calls total
        assert mock_func.call_count == 3
        assert mock_sleep.call_count == 2

def test_retry_non_retryable_error():
    # Fail with error that should NOT be retried
    mock_func = MagicMock(side_effect=ValueError("Normal error"))

    @retry_with_backoff(max_retries=3, base_delay=0.1)
    def decorated_func():
        return mock_func()

    with patch("time.sleep") as mock_sleep:
        with pytest.raises(ValueError, match="Normal error"):
            decorated_func()

        assert mock_func.call_count == 1
        assert mock_sleep.call_count == 0

def test_retry_case_insensitivity():
    # Test "RESOURCE_EXHAUSTED" in caps
    mock_func = MagicMock(side_effect=[Exception("RESOURCE_EXHAUSTED"), "success"])

    @retry_with_backoff(max_retries=1, base_delay=0.1)
    def decorated_func():
        return mock_func()

    with patch("time.sleep") as mock_sleep:
        result = decorated_func()
        assert result == "success"
        assert mock_func.call_count == 2
