import os
import pytest
from unittest.mock import patch, MagicMock
from src.core.llm_config import LLMConfigManager

# We use the real yaml if available, otherwise mock it for CI environments without it.
# However, for real file tests, it's better if it's available.
try:
    import yaml
except ImportError:
    yaml = MagicMock()

@pytest.fixture
def config_mgr(tmp_path):
    """Fixture to provide a LLMConfigManager instance in an isolated root directory."""
    return LLMConfigManager(root_dir=str(tmp_path))

def test_init_default_root():
    # Mock load_dotenv to prevent interaction with the real project root's .env
    with patch("src.core.llm_config.load_dotenv") as mock_load_dotenv:
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
    assert config_mgr.load_config() == {}

def test_load_config_valid(config_mgr):
    data = {"active_provider": "openai", "providers": {"openai": {"model": "gpt-4"}}}

    # If yaml is mocked, we still need to patch it in src.core.llm_config
    if isinstance(yaml, MagicMock):
        with patch("src.core.llm_config.yaml.safe_load", return_value=data):
            # We need the file to exist for load_config to proceed
            with open(config_mgr.config_path, "w", encoding="utf-8") as f:
                f.write("dummy content")
            assert config_mgr.load_config() == data
    else:
        with open(config_mgr.config_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f)
        assert config_mgr.load_config() == data

def test_load_config_malformed(config_mgr):
    # Write invalid content to the config path
    with open(config_mgr.config_path, "w", encoding="utf-8") as f:
        f.write("invalid: yaml: :")

    # If yaml is a MagicMock, we must mock safe_load and YAMLError
    if isinstance(yaml, MagicMock):
        class MockYAMLError(Exception):
            pass
        with patch("src.core.llm_config.yaml.YAMLError", MockYAMLError):
            with patch("src.core.llm_config.yaml.safe_load", side_effect=MockYAMLError("YAML error")):
                assert config_mgr.load_config() == {}
    else:
        assert config_mgr.load_config() == {}

def test_save_config(config_mgr):
    data = {"test": "data"}

    if isinstance(yaml, MagicMock):
        with patch("src.core.llm_config.yaml.dump") as mock_dump:
            config_mgr.save_config(data)
            mock_dump.assert_called_once()
            assert mock_dump.call_args[0][0] == data
    else:
        config_mgr.save_config(data)
        with open(config_mgr.config_path, "r", encoding="utf-8") as f:
            assert yaml.safe_load(f) == data

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
