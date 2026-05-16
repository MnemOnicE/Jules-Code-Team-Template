import os
import sys
from unittest.mock import patch, MagicMock
import tempfile
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'template_source', 'scripts')))
from health_check import (
    check_agents_directory,
    check_core_dependencies,
    check_agent_configs,
    check_engine_integrity,
    run_health_check
)

def test_check_agents_directory_missing_agents(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    passed, message = check_agents_directory()
    assert passed is False
    assert ".agents directory not found" in message

def test_check_agents_directory_missing_required_dirs(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    agents_dir = tmp_path / ".agents"
    agents_dir.mkdir()
    # Create some but not all
    (agents_dir / "config").mkdir()

    passed, message = check_agents_directory()
    assert passed is False
    assert "Missing directories:" in message
    assert "engine" in message
    assert "rules" in message

def test_check_agents_directory_success(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    agents_dir = tmp_path / ".agents"
    agents_dir.mkdir()
    for dir_name in ['config', 'engine', 'rules', 'workflows', 'memory']:
        (agents_dir / dir_name).mkdir()

    passed, message = check_agents_directory()
    assert passed is True
    assert "Directory structure OK" in message

@patch('importlib.util.find_spec')
def test_check_core_dependencies_missing_modules(mock_find_spec):
    # Simulate missing 'dotenv'
    def side_effect(module_name):
        if module_name == 'dotenv':
            return None
        return MagicMock()
    mock_find_spec.side_effect = side_effect

    passed, message = check_core_dependencies()
    assert passed is False
    assert "Missing modules: dotenv" in message

@patch('importlib.util.find_spec')
def test_check_core_dependencies_success(mock_find_spec):
    mock_find_spec.return_value = MagicMock() # All modules found

    passed, message = check_core_dependencies()
    assert passed is True
    assert "Core dependencies OK" in message

def test_check_agent_configs_missing_dir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    passed, message = check_agent_configs()
    assert passed is False
    assert "Config directory not found" in message

def test_check_agent_configs_missing_configs(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    config_dir = tmp_path / ".agents" / "config"
    config_dir.mkdir(parents=True)
    # Create one but not all
    (config_dir / "brain.md").write_text("brain config")

    passed, message = check_agent_configs()
    assert passed is False
    assert "Missing configs:" in message
    assert "sentinel.md" in message
    assert "boom.md" in message

def test_check_agent_configs_success(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    config_dir = tmp_path / ".agents" / "config"
    config_dir.mkdir(parents=True)
    for config in ['brain.md', 'sentinel.md', 'boom.md']:
        (config_dir / config).write_text("config")

    passed, message = check_agent_configs()
    assert passed is True
    assert "Agent configs OK" in message

def test_check_engine_integrity_missing_main(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    engine_dir = tmp_path / ".agents" / "engine"
    engine_dir.mkdir(parents=True)

    passed, message = check_engine_integrity()
    assert passed is False
    assert "Engine main.py not found" in message

@patch('importlib.util.spec_from_file_location')
def test_check_engine_integrity_load_error(mock_spec_from_file, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    engine_dir = tmp_path / ".agents" / "engine"
    engine_dir.mkdir(parents=True)
    (engine_dir / "main.py").write_text("print('test')")

    mock_spec_from_file.return_value = None

    passed, message = check_engine_integrity()
    assert passed is False
    assert "Cannot load engine module" in message

@patch('importlib.util.spec_from_file_location')
def test_check_engine_integrity_syntax_error(mock_spec_from_file, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    engine_dir = tmp_path / ".agents" / "engine"
    engine_dir.mkdir(parents=True)
    (engine_dir / "main.py").write_text("invalid syntax!")

    # Mock the spec and loader so compile() raises a SyntaxError
    mock_spec = MagicMock()
    mock_spec.loader.get_source.return_value = "invalid syntax!"
    mock_spec_from_file.return_value = mock_spec

    passed, message = check_engine_integrity()
    assert passed is False
    assert "Engine check failed:" in message

@patch('importlib.util.spec_from_file_location')
def test_check_engine_integrity_success(mock_spec_from_file, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    engine_dir = tmp_path / ".agents" / "engine"
    engine_dir.mkdir(parents=True)
    (engine_dir / "main.py").write_text("def run():\n    pass\n")

    # Mock the spec and loader so compile() succeeds
    mock_spec = MagicMock()
    mock_spec.loader.get_source.return_value = "def run():\n    pass\n"
    mock_spec_from_file.return_value = mock_spec

    passed, message = check_engine_integrity()
    assert passed is True
    assert "Engine integrity OK" in message

@patch('health_check.check_agents_directory')
@patch('health_check.check_core_dependencies')
@patch('health_check.check_agent_configs')
@patch('health_check.check_engine_integrity')
@patch('builtins.print')
def test_run_health_check_all_pass(mock_print, mock_engine, mock_configs, mock_core, mock_agents):
    mock_agents.return_value = (True, "OK")
    mock_core.return_value = (True, "OK")
    mock_configs.return_value = (True, "OK")
    mock_engine.return_value = (True, "OK")

    result = run_health_check()
    assert result == 0
    # verify that the final success message was printed
    mock_print.assert_any_call("🎉 All checks passed! System is healthy.")

@patch('health_check.check_agents_directory')
@patch('health_check.check_core_dependencies')
@patch('health_check.check_agent_configs')
@patch('health_check.check_engine_integrity')
@patch('builtins.print')
def test_run_health_check_some_fail(mock_print, mock_engine, mock_configs, mock_core, mock_agents):
    mock_agents.return_value = (True, "OK")
    mock_core.return_value = (False, "Missing something")
    mock_configs.return_value = (True, "OK")
    mock_engine.return_value = (True, "OK")

    result = run_health_check()
    assert result == 1
    mock_print.assert_any_call("⚠️  Some checks failed. Run 'squad --diagnose' for detailed help.")

@patch('health_check.check_agents_directory')
@patch('health_check.check_core_dependencies')
@patch('health_check.check_agent_configs')
@patch('health_check.check_engine_integrity')
@patch('builtins.print')
def test_run_health_check_exception(mock_print, mock_engine, mock_configs, mock_core, mock_agents):
    mock_agents.side_effect = Exception("Unexpected error")
    mock_core.return_value = (True, "OK")
    mock_configs.return_value = (True, "OK")
    mock_engine.return_value = (True, "OK")

    result = run_health_check()
    assert result == 1
    mock_print.assert_any_call("   Error: Unexpected error")
