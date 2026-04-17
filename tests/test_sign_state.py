import pytest
import hashlib
from unittest.mock import patch, mock_open
from sign_state import sign_state

def test_sign_state_file_not_found(capsys):
    """Test handling of FileNotFoundError from get_session_json_path."""
    with patch("sign_state.get_session_json_path", side_effect=FileNotFoundError):
        with pytest.raises(SystemExit) as excinfo:
            sign_state()

        assert excinfo.value.code == 1
        captured = capsys.readouterr()
        assert "ERROR: session.json not found. State cannot be signed." in captured.out

def test_sign_state_target_file_none(capsys):
    """Test handling of None return from get_session_json_path."""
    with patch("sign_state.get_session_json_path", return_value=None):
        with pytest.raises(SystemExit) as excinfo:
            sign_state()

        assert excinfo.value.code == 1
        captured = capsys.readouterr()
        assert "ERROR: session.json not found. State cannot be signed." in captured.out

def test_sign_state_happy_path(tmp_path, capsys):
    """Test successful state signing with valid file content."""
    test_content = b"hello world session content"
    session_file = tmp_path / "session.json"
    session_file.write_bytes(test_content)

    expected_hash = hashlib.sha256(test_content).hexdigest()[:8]

    with patch("sign_state.get_session_json_path", return_value=str(session_file)):
        sign_state()

        captured = capsys.readouterr()
        assert captured.out.strip() == expected_hash

def test_sign_state_generic_exception(capsys):
    """Test handling of generic exceptions during file reading."""
    with patch("sign_state.get_session_json_path", return_value="fake_path.json"):
        with patch("builtins.open", side_effect=Exception("Read failure")):
            with pytest.raises(SystemExit) as excinfo:
                sign_state()

            assert excinfo.value.code == 1
            captured = capsys.readouterr()
            assert "ERROR: Could not sign state. Read failure" in captured.out
