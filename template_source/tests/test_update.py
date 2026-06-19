import importlib.util
from pathlib import Path


def load_update_module(path):
    spec = importlib.util.spec_from_file_location("update", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_compare_versions():
    update = load_update_module(Path(__file__).resolve().parents[1] / "scripts" / "update.py")
    assert update.compare_versions("v1.0.1", "v1.0.0") == 1
    assert update.compare_versions("1.0.0", "v1.0.0") == 0
    assert update.compare_versions("v0.9.9", "v1.0.0") == -1
    assert update.compare_versions("invalid", "v1.0.0") == 0

from unittest.mock import patch, mock_open, MagicMock
import json

update_module = load_update_module(Path(__file__).resolve().parents[1] / "scripts" / "update.py")

@patch('pathlib.Path.exists')
@patch('builtins.open', new_callable=mock_open, read_data='{"version": "1.2.3"}')
def test_get_current_version_success(mock_file, mock_exists):
    mock_exists.return_value = True
    assert update_module.get_current_version() == "1.2.3"

@patch('pathlib.Path.exists')
@patch('builtins.open', new_callable=mock_open, read_data='{"name": "test"}')
def test_get_current_version_no_version(mock_file, mock_exists):
    mock_exists.return_value = True
    assert update_module.get_current_version() is None

@patch('pathlib.Path.exists')
@patch('builtins.open', new_callable=mock_open, read_data='{invalid_json')
def test_get_current_version_invalid_json(mock_file, mock_exists):
    mock_exists.return_value = True
    assert update_module.get_current_version() is None

@patch('pathlib.Path.exists')
def test_get_current_version_no_file(mock_exists):
    mock_exists.return_value = False
    assert update_module.get_current_version() is None

@patch('pathlib.Path.exists')
@patch('builtins.open')
def test_get_current_version_read_error(mock_open, mock_exists):
    mock_exists.return_value = True
    mock_open.side_effect = PermissionError("Access denied")
    assert update_module.get_current_version() is None
