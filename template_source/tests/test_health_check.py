import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the module to be tested
from health_check import check_agents_directory

def test_check_agents_directory_not_found(monkeypatch):
    """Test when .agents directory does not exist."""

    original_exists = Path.exists

    def mock_exists(self):
        if self.parts and self.parts[0] == '.agents' and len(self.parts) == 1:
            return False
        return original_exists(self)

    monkeypatch.setattr(Path, 'exists', mock_exists)

    passed, message = check_agents_directory()
    assert not passed
    assert message == ".agents directory not found"


def test_check_agents_directory_missing_required(monkeypatch):
    """Test when .agents directory exists but some required directories are missing."""

    original_exists = Path.exists

    def mock_exists(self):
        # We need to handle paths consistently. In health_check.py, it uses `Path('.agents')`
        # and `agents_dir / dir_name`

        # When printing `self`, it will be '.agents' or '.agents/config' (depending on OS path separator)
        path_str = str(self).replace('\\', '/')
        if path_str == '.agents':
            return True
        elif path_str in ['.agents/engine', '.agents/memory']:
            return False
        elif path_str.startswith('.agents/'):
            return True

        return original_exists(self)

    monkeypatch.setattr(Path, 'exists', mock_exists)

    passed, message = check_agents_directory()
    assert not passed
    assert "Missing directories:" in message
    assert "engine" in message
    assert "memory" in message


def test_check_agents_directory_all_ok(monkeypatch):
    """Test when .agents directory and all required directories exist."""

    original_exists = Path.exists

    def mock_exists(self):
        path_str = str(self).replace('\\', '/')
        if path_str == '.agents' or path_str.startswith('.agents/'):
            return True
        return original_exists(self)

    monkeypatch.setattr(Path, 'exists', mock_exists)

    passed, message = check_agents_directory()
    assert passed
    assert message == "Directory structure OK"
