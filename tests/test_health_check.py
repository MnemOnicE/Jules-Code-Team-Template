import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys

from template_source.scripts.health_check import check_engine_integrity

def test_check_engine_integrity_success(monkeypatch):
    monkeypatch.setattr(Path, "exists", lambda x: True)

    mock_spec = MagicMock()
    mock_spec.loader.get_source.return_value = "print('hello')"

    with patch("template_source.scripts.health_check.importlib.util.spec_from_file_location", return_value=mock_spec):
        with patch("builtins.compile") as mock_compile:
            success, message = check_engine_integrity()
            assert success is True
            assert message == "Engine integrity OK"
            mock_compile.assert_called_once()

def test_check_engine_integrity_main_missing(monkeypatch):
    monkeypatch.setattr(Path, "exists", lambda x: False)

    success, message = check_engine_integrity()
    assert success is False
    assert message == "Engine main.py not found"

def test_check_engine_integrity_spec_none(monkeypatch):
    monkeypatch.setattr(Path, "exists", lambda x: True)

    with patch("template_source.scripts.health_check.importlib.util.spec_from_file_location", return_value=None):
        success, message = check_engine_integrity()
        assert success is False
        assert message == "Cannot load engine module"

def test_check_engine_integrity_compile_error(monkeypatch):
    monkeypatch.setattr(Path, "exists", lambda x: True)

    mock_spec = MagicMock()
    mock_spec.loader.get_source.return_value = "invalid syntax"

    with patch("template_source.scripts.health_check.importlib.util.spec_from_file_location", return_value=mock_spec):
        with patch("builtins.compile", side_effect=Exception("mocked syntax error")):
            success, message = check_engine_integrity()
            assert success is False
            assert "Engine check failed: mocked syntax error" in message
