import os
import pytest
from unittest.mock import patch, MagicMock, mock_open
from src.core.llm_config import LLMConfigManager

@pytest.fixture
def config_mgr(tmp_path):
    """Fixture to provide a LLMConfigManager instance in an isolated root directory."""
    return LLMConfigManager(root_dir=str(tmp_path))

def test_init_default_root():
    with patch("src.core.llm_config.load_dotenv"):
        mgr = LLMConfigManager()
        assert os.path.isabs(mgr.root_dir)
        assert mgr.env_path == os.path.join(mgr.root_dir, '.env')
        assert mgr.config_path == os.path.join(mgr.root_dir, 'llm_config.yaml')

def test_init_custom_root(tmp_path):
    custom_root = str(tmp_path)
    mgr = LLMConfigManager(root_dir=custom_root)
    assert mgr.root_dir == custom_root
    assert mgr.env_path == os.path.join(custom_root, '.env')
    assert mgr.config_path == os.path.join(custom_root, 'llm_config.yaml')

def test_init_loads_dotenv(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("TEST_VAR=test_value")

    # Patch load_dotenv within the module it's used in
    with patch("src.core.llm_config.load_dotenv") as mock_load_dotenv:
        LLMConfigManager(root_dir=str(tmp_path))
        mock_load_dotenv.assert_called_once_with(str(env_file))

def test_get_api_key(config_mgr):
    with patch.dict(os.environ, {"TEST_API_KEY": "secret"}):
        assert config_mgr.get_api_key("TEST_API_KEY") == "secret"
        assert config_mgr.get_api_key("NON_EXISTENT_KEY") is None

def test_set_api_key(config_mgr):
    with patch("src.core.llm_config.set_key") as mock_set_key:
        with patch.dict(os.environ, {}, clear=True):
            config_mgr.set_api_key("NEW_KEY", "new_value")

            assert os.environ["NEW_KEY"] == "new_value"
            mock_set_key.assert_called_once_with(config_mgr.env_path, "NEW_KEY", "new_value")
            # set_api_key explicitly creates the file if it doesn't exist
            assert os.path.exists(config_mgr.env_path)

def test_load_config_missing(config_mgr):
    # No file created in tmp_path, should return empty dict
    assert config_mgr.load_config() == {}

def test_load_config_valid(config_mgr):
    data = {"active_provider": "openai", "providers": {"openai": {"model": "gpt-4"}}}

    # Mocking yaml within src.core.llm_config to handle environments without PyYAML
    with patch("src.core.llm_config.yaml.safe_load", return_value=data):
        with patch("builtins.open", mock_open(read_data="dummy")):
            # We must also mock os.path.exists for the config_path
            with patch("os.path.exists", side_effect=lambda p: p == config_mgr.config_path or os.path.exists(p)):
                assert config_mgr.load_config() == data

def test_load_config_malformed(config_mgr):
    # Define a mock exception that behaves like yaml.YAMLError
    class MockYAMLError(Exception):
        pass

    with patch("src.core.llm_config.yaml.YAMLError", MockYAMLError):
        with patch("src.core.llm_config.yaml.safe_load", side_effect=MockYAMLError("YAML error")):
            with patch("builtins.open", mock_open(read_data="dummy")):
                with patch("os.path.exists", side_effect=lambda p: p == config_mgr.config_path or os.path.exists(p)):
                    assert config_mgr.load_config() == {}

def test_save_config(config_mgr):
    data = {"test": "data"}

    with patch("src.core.llm_config.yaml.dump") as mock_dump:
        with patch("builtins.open", mock_open()) as mocked_file:
            config_mgr.save_config(data)
            mock_dump.assert_called_once()
            assert mock_dump.call_args[0][0] == data

def test_get_provider_config(config_mgr):
    data = {"providers": {"openai": {"model": "gpt-4"}}}

    with patch.object(LLMConfigManager, 'load_config', return_value=data):
        assert config_mgr.get_provider_config("openai") == {"model": "gpt-4"}
        assert config_mgr.get_provider_config("anthropic") == {}

def test_set_provider_config(config_mgr):
    initial_data = {"providers": {"openai": {"model": "gpt-4"}}}

    with patch.object(LLMConfigManager, 'load_config', return_value=initial_data):
        with patch.object(LLMConfigManager, 'save_config') as mock_save:
            config_mgr.set_provider_config("gemini", {"api_key": "abc"})

            expected_data = {
                "providers": {
                    "openai": {"model": "gpt-4"},
                    "gemini": {"api_key": "abc"}
                }
            }
            mock_save.assert_called_once_with(expected_data)

def test_get_active_provider(config_mgr):
    data = {"active_provider": "openai"}

    with patch.object(LLMConfigManager, 'load_config', return_value=data):
        assert config_mgr.get_active_provider() == "openai"

def test_set_active_provider(config_mgr):
    initial_data = {}

    with patch.object(LLMConfigManager, 'load_config', return_value=initial_data):
        with patch.object(LLMConfigManager, 'save_config') as mock_save:
            config_mgr.set_active_provider("jules")

            expected_data = {"active_provider": "jules"}
            mock_save.assert_called_once_with(expected_data)
