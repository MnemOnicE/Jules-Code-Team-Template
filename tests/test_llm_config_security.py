import subprocess
import pytest
from unittest.mock import patch
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

    with patch('builtins.input', side_effect=inputs):
        with patch('subprocess.run') as mock_run:
            # We don't want it to actually fail or do anything
            configure_llm_providers()

            # Check if all subprocess.run calls had check=True
            assert mock_run.call_count == 4
            for call in mock_run.call_args_list:
                args, kwargs = call
                assert kwargs.get('check') is True

if __name__ == "__main__":
    test_configure_llm_providers_subprocess_calls_with_check_true()
