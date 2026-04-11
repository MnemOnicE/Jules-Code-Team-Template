import json
import urllib.request
from unittest.mock import MagicMock, patch
from pathlib import Path
import importlib.util

def load_update_module():
    path = Path(__file__).resolve().parents[1] / "scripts" / "update.py"
    spec = importlib.util.spec_from_file_location("update", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

@patch("urllib.request.urlopen")
def test_get_latest_version_success(mock_urlopen):
    update = load_update_module()

    # Mock response
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({"tag_name": "v1.2.3"}).encode("utf-8")
    mock_response.__enter__.return_value = mock_response
    mock_urlopen.return_value = mock_response

    version = update.get_latest_version()

    assert version == "v1.2.3"
    mock_urlopen.assert_called_once()
    args, kwargs = mock_urlopen.call_args
    assert args[0].full_url == "https://api.github.com/repos/MnemOnicE/Jules-Code-Team-Template/releases/latest"
    assert args[0].headers["User-Agent"] == "Jules-Code-Team-Template-Updater"
    assert kwargs["timeout"] == 10

@patch("urllib.request.urlopen")
def test_get_latest_version_failure(mock_urlopen):
    update = load_update_module()

    # Simulate exception
    mock_urlopen.side_effect = Exception("Network error")

    version = update.get_latest_version()

    assert version is None
