import pytest
from unittest.mock import patch, mock_open
import sys
import hashlib

from sign_state import sign_state

def test_sign_state_file_not_found():
    with patch("sign_state.get_session_json_path", side_effect=FileNotFoundError):
        with patch("builtins.print") as mock_print:
            with pytest.raises(SystemExit) as e:
                sign_state()
            assert e.value.code == 1
            mock_print.assert_called_with("ERROR: session.json not found. State cannot be signed.")

def test_sign_state_no_target_file():
    with patch("sign_state.get_session_json_path", return_value=None):
        with patch("builtins.print") as mock_print:
            with pytest.raises(SystemExit) as e:
                sign_state()
            assert e.value.code == 1
            mock_print.assert_called_with("ERROR: session.json not found. State cannot be signed.")

def test_sign_state_success():
    fake_content = b"fake_json_data"
    expected_hash = hashlib.sha256(fake_content).hexdigest()[:8]

    with patch("sign_state.get_session_json_path", return_value="dummy/session.json"):
        with patch("builtins.open", mock_open(read_data=fake_content)):
            with patch("builtins.print") as mock_print:
                sign_state()
                mock_print.assert_called_with(expected_hash)

def test_sign_state_read_exception():
    with patch("sign_state.get_session_json_path", return_value="dummy/session.json"):
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            with patch("builtins.print") as mock_print:
                with pytest.raises(SystemExit) as e:
                    sign_state()
                assert e.value.code == 1
                mock_print.assert_called_with("ERROR: Could not sign state. Permission denied")
