import subprocess
import pytest
from unittest.mock import patch, MagicMock
from src.core.llm_config import configure_llm_providers

def test_configure_llm_providers_subprocess_calls_with_check_true():
    # Mock input to select all providers that call subprocess.run
    inputs = [
        'y', 'openai_key',      # OpenAI
        'y', 'gemini_key',      # Gemini
        'n',                    # Jules (no subprocess)
        'y', 'llama3',          # Ollama
        'y', './models/model.gguf', # LlamaCpp
    ]

    # Mock LLMConfigManager to avoid filesystem side effects
    # Mock os.environ to avoid environment side effects
    # Mock subprocess.run to verify arguments
    with patch('builtins.input', side_effect=inputs), \
         patch('src.core.llm_config.LLMConfigManager') as mock_mgr_class, \
         patch('os.environ', {}), \
         patch('subprocess.run') as mock_run:

            # Setup the mock instance
            mock_mgr = MagicMock()
            mock_mgr_class.return_value = mock_mgr
            mock_mgr.load_config.return_value = {}

            configure_llm_providers()

            # Check if all subprocess.run calls had check=True
            assert mock_run.call_count == 4
            for call in mock_run.call_args_list:
                args, kwargs = call
                assert kwargs.get('check') is True

if __name__ == "__main__":
    test_configure_llm_providers_subprocess_calls_with_check_true()
