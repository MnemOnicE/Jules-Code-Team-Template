import pytest
import os
import stat
from unittest.mock import patch, MagicMock
from core.llm_config import LLMConfigManager

def test_set_api_key_creates_env_with_secure_permissions(tmp_path):
    env_path = tmp_path / ".env"

    with patch('core.llm_config.os.path.exists', return_value=False):
        # We need to mock set_key and os.environ as we're just testing the file creation
        with patch('core.llm_config.set_key'):
            # Also need to mock os.path.exists specifically inside the set_api_key function
            # since it uses it directly without class state.
            mgr = LLMConfigManager(root_dir=str(tmp_path))
            mgr.env_path = str(env_path)

            # Patch os.environ so we don't pollute the actual environment
            with patch.dict('core.llm_config.os.environ', {}, clear=True):
                # The actual test execution
                mgr.set_api_key("TEST_KEY", "test_value")

    # Now verify the file exists and has the correct permissions
    assert os.path.exists(str(env_path))

    # Check permissions
    st = os.stat(str(env_path))

    # Assert owner read/write (0o600)
    assert bool(st.st_mode & stat.S_IRUSR) is True
    assert bool(st.st_mode & stat.S_IWUSR) is True

    # Assert NO read/write/execute for group and others
    assert bool(st.st_mode & stat.S_IRGRP) is False
    assert bool(st.st_mode & stat.S_IWGRP) is False
    assert bool(st.st_mode & stat.S_IXGRP) is False
    assert bool(st.st_mode & stat.S_IROTH) is False
    assert bool(st.st_mode & stat.S_IWOTH) is False
    assert bool(st.st_mode & stat.S_IXOTH) is False
