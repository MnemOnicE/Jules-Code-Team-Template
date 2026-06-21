import pytest
from pathlib import Path
from template_source.scripts.health_check import check_agents_directory

def test_check_agents_directory_happy_path(monkeypatch, tmp_path):
    # Mock the Path class to use the tmp_path as the base
    # But wait, `health_check.py` uses `Path('.agents')` directly.
    # It's better to use monkeypatch to change the current working directory
    # or mock `Path.exists` directly. Let's use tmp_path and monkeypatch.chdir.

    monkeypatch.chdir(tmp_path)

    # Create the structure
    agents_dir = tmp_path / '.agents'
    agents_dir.mkdir()
    required_dirs = ['config', 'engine', 'rules', 'workflows', 'memory']
    for d in required_dirs:
        (agents_dir / d).mkdir()

    passed, message = check_agents_directory()
    assert passed is True
    assert message == "Directory structure OK"

def test_check_agents_directory_missing_base(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    # Don't create the .agents directory

    passed, message = check_agents_directory()
    assert passed is False
    assert message == ".agents directory not found"

def test_check_agents_directory_missing_subdirs(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    # Create the base directory
    agents_dir = tmp_path / '.agents'
    agents_dir.mkdir()

    # Create only some of the subdirectories
    (agents_dir / 'config').mkdir()
    (agents_dir / 'engine').mkdir()
    # Missing: rules, workflows, memory

    passed, message = check_agents_directory()
    assert passed is False
    assert "Missing directories" in message
    assert "rules" in message
    assert "workflows" in message
    assert "memory" in message

from unittest.mock import patch
from template_source.scripts.health_check import check_core_dependencies, check_agent_configs, check_engine_integrity

def test_check_core_dependencies_happy_path():
    with patch('importlib.util.find_spec') as mock_find_spec:
        mock_find_spec.return_value = True
        passed, message = check_core_dependencies()
        assert passed is True
        assert message == "Core dependencies OK"

def test_check_core_dependencies_missing():
    with patch('importlib.util.find_spec') as mock_find_spec:
        mock_find_spec.return_value = None
        passed, message = check_core_dependencies()
        assert passed is False
        assert "yaml" in message
        assert "dotenv" in message
        assert "jsonschema" in message

def test_check_agent_configs_happy_path(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    config_dir = tmp_path / '.agents' / 'config'
    config_dir.mkdir(parents=True)
    for config in ['brain.md', 'sentinel.md', 'boom.md']:
        (config_dir / config).touch()

    passed, message = check_agent_configs()
    assert passed is True
    assert message == "Agent configs OK"

def test_check_agent_configs_missing_dir(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    passed, message = check_agent_configs()
    assert passed is False
    assert message == "Config directory not found"

def test_check_agent_configs_missing_files(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    config_dir = tmp_path / '.agents' / 'config'
    config_dir.mkdir(parents=True)
    (config_dir / 'brain.md').touch()

    passed, message = check_agent_configs()
    assert passed is False
    assert "sentinel.md" in message
    assert "boom.md" in message

def test_check_engine_integrity_happy_path(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    engine_dir = tmp_path / '.agents' / 'engine'
    engine_dir.mkdir(parents=True)
    main_py = engine_dir / 'main.py'
    main_py.write_text("print('hello')")

    passed, message = check_engine_integrity()
    assert passed is True
    assert message == "Engine integrity OK"

def test_check_engine_integrity_missing_file(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    passed, message = check_engine_integrity()
    assert passed is False
    assert message == "Engine main.py not found"

def test_check_engine_integrity_syntax_error(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    engine_dir = tmp_path / '.agents' / 'engine'
    engine_dir.mkdir(parents=True)
    main_py = engine_dir / 'main.py'
    # Invalid python code
    main_py.write_text("print('hello'")

    passed, message = check_engine_integrity()
    assert passed is False
    assert "Engine check failed" in message

from unittest.mock import patch
from template_source.scripts.health_check import run_health_check

def test_run_health_check_all_passed(monkeypatch):
    monkeypatch.setattr('template_source.scripts.health_check.check_agents_directory', lambda: (True, "OK"))
    monkeypatch.setattr('template_source.scripts.health_check.check_core_dependencies', lambda: (True, "OK"))
    monkeypatch.setattr('template_source.scripts.health_check.check_agent_configs', lambda: (True, "OK"))
    monkeypatch.setattr('template_source.scripts.health_check.check_engine_integrity', lambda: (True, "OK"))

    assert run_health_check() == 0

def test_run_health_check_some_failed(monkeypatch):
    monkeypatch.setattr('template_source.scripts.health_check.check_agents_directory', lambda: (True, "OK"))
    monkeypatch.setattr('template_source.scripts.health_check.check_core_dependencies', lambda: (False, "Failed"))
    monkeypatch.setattr('template_source.scripts.health_check.check_agent_configs', lambda: (True, "OK"))
    monkeypatch.setattr('template_source.scripts.health_check.check_engine_integrity', lambda: (True, "OK"))

    assert run_health_check() == 1

def test_run_health_check_exception(monkeypatch):
    def raise_exception():
        raise ValueError("Something went wrong")

    monkeypatch.setattr('template_source.scripts.health_check.check_agents_directory', lambda: (True, "OK"))
    monkeypatch.setattr('template_source.scripts.health_check.check_core_dependencies', raise_exception)
    monkeypatch.setattr('template_source.scripts.health_check.check_agent_configs', lambda: (True, "OK"))
    monkeypatch.setattr('template_source.scripts.health_check.check_engine_integrity', lambda: (True, "OK"))

    assert run_health_check() == 1
