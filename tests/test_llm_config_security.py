import pytest
import subprocess
from unittest.mock import patch, MagicMock
from src.core.llm_config import configure_llm_providers

def test_configure_llm_providers_handle_install_failure(capsys):
    """
    Test that configure_llm_providers handles subprocess.CalledProcessError
    when installing an SDK.
    """
    # Mock inputs to select OpenAI and skip others
    # 1. Use OpenAI? (y)
    # 2. OpenAI API Key? (test_key)
    # 3. Use Gemini? (n)
    # 4. Use Jules API? (n)
    # 5. Use Ollama? (n)
    # 6. Use Llama.cpp? (n)
    inputs = ['y', 'test_key', 'n', 'n', 'n', 'n']

    with patch('builtins.input', side_effect=inputs):
        with patch('subprocess.run') as mock_run:
            # Simulate failure
            mock_run.side_effect = subprocess.CalledProcessError(1, 'pip install openai')

            # We also need to mock LLMConfigManager to avoid side effects on filesystem
            with patch('src.core.llm_config.LLMConfigManager') as mock_mgr:
                configure_llm_providers()

                # Check if it was called with check=True
                mock_run.assert_called()
                args, kwargs = mock_run.call_args
                assert kwargs.get('check') is True

                # Check if error message was printed
                captured = capsys.readouterr()
                assert "❌ Failed to install openai sdk. Please install it manually." in captured.out

def test_configure_llm_providers_multiple_failures(capsys):
    """
    Test that configure_llm_providers handles failures for multiple providers.
    """
    # Select OpenAI and Gemini
    inputs = ['y', 'key1', 'y', 'key2', 'n', 'n', 'n']

    with patch('builtins.input', side_effect=inputs):
        with patch('subprocess.run') as mock_run:
            # Simulate failure
            mock_run.side_effect = subprocess.CalledProcessError(1, 'pip install')

            with patch('src.core.llm_config.LLMConfigManager') as mock_mgr:
                configure_llm_providers()

                captured = capsys.readouterr()
                assert "❌ Failed to install openai sdk. Please install it manually." in captured.out
                assert "❌ Failed to install google-genai sdk. Please install it manually." in captured.out
