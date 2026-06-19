import hashlib
import pytest
from unittest.mock import patch, mock_open
import sys

from sign_state import sign_state

def test_sign_state_success(tmp_path, capsys):
    # Create a temporary session.json file with known content
    test_content = b'{"state": "test"}'
    test_file = tmp_path / "session.json"
    test_file.write_bytes(test_content)

    expected_hash = hashlib.sha256(test_content).hexdigest()[:8]

    with patch('sign_state.get_session_json_path', return_value=str(test_file)):
        sign_state()

    captured = capsys.readouterr()
    assert expected_hash in captured.out

def test_sign_state_file_not_found(capsys):
    with patch('sign_state.get_session_json_path', side_effect=FileNotFoundError):
        with pytest.raises(SystemExit) as excinfo:
            sign_state()

    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "ERROR: session.json not found. State cannot be signed." in captured.out

def test_sign_state_empty_target_file(capsys):
    with patch('sign_state.get_session_json_path', return_value=""):
        with pytest.raises(SystemExit) as excinfo:
            sign_state()

    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "ERROR: session.json not found. State cannot be signed." in captured.out

def test_sign_state_exception(capsys):
    with patch('sign_state.get_session_json_path', return_value="dummy_path"):
        with patch('sign_state.open', side_effect=Exception("Mocked error")):
            with pytest.raises(SystemExit) as excinfo:
                sign_state()

    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "ERROR: Could not sign state. Mocked error" in captured.out
