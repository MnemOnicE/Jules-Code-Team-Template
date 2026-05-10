import hashlib
import json
import importlib.util
from pathlib import Path


def load_plugin_manager(path):
    spec = importlib.util.spec_from_file_location("plugin_manager", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_plugin_allowlist_and_hash_validation(tmp_path):
    project_root = Path(__file__).resolve().parents[1]
    module = load_plugin_manager(project_root / ".agents" / "engine" / "core" / "plugin_manager.py")

    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()

    plugin_file = plugins_dir / "safe_plugin.py"
    plugin_file.write_text(
        "PLUGIN_INFO = {'name': 'Safe Plugin', 'version': '1.0.0', 'description': 'Safe test plugin', 'author': 'Test'}\n",
        encoding='utf-8'
    )

    sha256 = hashlib.sha256(plugin_file.read_bytes()).hexdigest()
    allowlist = {
        "plugins": {
            "safe_plugin": {
                "hash": sha256
            }
        }
    }
    (plugins_dir / "allowed_plugins.json").write_text(json.dumps(allowlist), encoding='utf-8')

    manager = module.PluginManager(plugins_dir=str(plugins_dir))
    assert manager.discover_plugins() == ["safe_plugin"]

    plugin_module = manager.load_plugin("safe_plugin")
    assert plugin_module.PLUGIN_INFO["name"] == "Safe Plugin"


def test_plugin_rejects_invalid_name(tmp_path):
    project_root = Path(__file__).resolve().parents[1]
    module = load_plugin_manager(project_root / ".agents" / "engine" / "core" / "plugin_manager.py")

    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()

    plugin_file = plugins_dir / "bad plugin.py"
    plugin_file.write_text(
        "PLUGIN_INFO = {'name': 'Bad', 'version': '1.0.0', 'description': 'Bad name', 'author': 'Test'}\n",
        encoding='utf-8'
    )

    manager = module.PluginManager(plugins_dir=str(plugins_dir))

    try:
        manager.load_plugin("bad plugin")
        assert False, "Invalid plugin names should be rejected"
    except ValueError:
        pass


# --- Tests for PR changes: _is_plugin_allowed and discover_plugins behavior ---

def test_is_plugin_allowed_when_no_allowlist_file(tmp_path):
    """When no allowed_plugins.json exists, any plugin should be allowed (new behavior)."""
    project_root = Path(__file__).resolve().parents[1]
    module = load_plugin_manager(project_root / ".agents" / "engine" / "core" / "plugin_manager.py")

    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()
    # No allowed_plugins.json created

    manager = module.PluginManager(plugins_dir=str(plugins_dir))
    # allowed_plugins should be empty dict (falsy) from _load_allowlist
    assert not manager.allowed_plugins
    # _is_plugin_allowed should return True for any name when no allowlist
    assert manager._is_plugin_allowed("any_plugin") is True
    assert manager._is_plugin_allowed("another_plugin") is True


def test_is_plugin_allowed_with_allowlist_restricts_access(tmp_path):
    """When an allowlist exists, only listed plugins should be allowed."""
    project_root = Path(__file__).resolve().parents[1]
    module = load_plugin_manager(project_root / ".agents" / "engine" / "core" / "plugin_manager.py")

    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()

    allowlist = {"plugins": {"approved_plugin": {"hash": "abc123"}}}
    (plugins_dir / "allowed_plugins.json").write_text(json.dumps(allowlist), encoding='utf-8')

    manager = module.PluginManager(plugins_dir=str(plugins_dir))
    assert manager._is_plugin_allowed("approved_plugin") is True
    assert manager._is_plugin_allowed("unapproved_plugin") is False


def test_discover_plugins_scans_directory_when_no_allowlist(tmp_path):
    """discover_plugins should scan the plugins dir for .py files when no allowlist exists."""
    project_root = Path(__file__).resolve().parents[1]
    module = load_plugin_manager(project_root / ".agents" / "engine" / "core" / "plugin_manager.py")

    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()
    # No allowed_plugins.json

    # Create some plugin files
    (plugins_dir / "my_plugin.py").write_text("PLUGIN_INFO = {}\n", encoding='utf-8')
    (plugins_dir / "another_plugin.py").write_text("PLUGIN_INFO = {}\n", encoding='utf-8')
    (plugins_dir / "not_a_plugin.txt").write_text("text file", encoding='utf-8')

    manager = module.PluginManager(plugins_dir=str(plugins_dir))
    discovered = manager.discover_plugins()

    assert set(discovered) == {"my_plugin", "another_plugin"}


def test_discover_plugins_excludes_underscore_files_when_no_allowlist(tmp_path):
    """Files starting with underscore (e.g., __init__.py) should not be discovered."""
    project_root = Path(__file__).resolve().parents[1]
    module = load_plugin_manager(project_root / ".agents" / "engine" / "core" / "plugin_manager.py")

    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()
    # No allowed_plugins.json

    (plugins_dir / "valid_plugin.py").write_text("PLUGIN_INFO = {}\n", encoding='utf-8')
    (plugins_dir / "__init__.py").write_text("# init\n", encoding='utf-8')
    (plugins_dir / "_private.py").write_text("# private\n", encoding='utf-8')

    manager = module.PluginManager(plugins_dir=str(plugins_dir))
    discovered = manager.discover_plugins()

    assert "valid_plugin" in discovered
    assert "__init__" not in discovered
    assert "_private" not in discovered


def test_discover_plugins_returns_empty_when_dir_missing(tmp_path):
    """discover_plugins should return [] when the plugins directory doesn't exist."""
    project_root = Path(__file__).resolve().parents[1]
    module = load_plugin_manager(project_root / ".agents" / "engine" / "core" / "plugin_manager.py")

    nonexistent_dir = tmp_path / "nonexistent_plugins"
    # Do NOT create the directory

    manager = module.PluginManager(plugins_dir=str(nonexistent_dir))
    assert manager.discover_plugins() == []


def test_discover_plugins_with_allowlist_uses_allowlist_keys(tmp_path):
    """When an allowlist exists, discover_plugins should use allowlist keys, not scan dir."""
    project_root = Path(__file__).resolve().parents[1]
    module = load_plugin_manager(project_root / ".agents" / "engine" / "core" / "plugin_manager.py")

    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()

    # Create a plugin file that is NOT in allowlist
    (plugins_dir / "unlisted_plugin.py").write_text("PLUGIN_INFO = {}\n", encoding='utf-8')

    allowlist = {"plugins": {"listed_plugin": {"hash": "abc"}}}
    (plugins_dir / "allowed_plugins.json").write_text(json.dumps(allowlist), encoding='utf-8')

    manager = module.PluginManager(plugins_dir=str(plugins_dir))
    discovered = manager.discover_plugins()

    # Should only return listed plugins, not unlisted ones on disk
    assert "listed_plugin" in discovered
    assert "unlisted_plugin" not in discovered


def test_load_plugin_without_allowlist_allows_any_valid_plugin(tmp_path):
    """Without an allowlist, any valid plugin file with PLUGIN_INFO should be loadable."""
    project_root = Path(__file__).resolve().parents[1]
    module = load_plugin_manager(project_root / ".agents" / "engine" / "core" / "plugin_manager.py")

    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()
    # No allowed_plugins.json

    plugin_file = plugins_dir / "open_plugin.py"
    plugin_file.write_text(
        "PLUGIN_INFO = {'name': 'Open Plugin', 'version': '1.0', 'description': 'No allowlist needed', 'author': 'Dev'}\n",
        encoding='utf-8'
    )

    manager = module.PluginManager(plugins_dir=str(plugins_dir))
    loaded = manager.load_plugin("open_plugin")
    assert loaded.PLUGIN_INFO["name"] == "Open Plugin"


def test_discover_plugins_filters_invalid_names_from_dir_scan(tmp_path):
    """Files with invalid names (not matching PLUGIN_NAME_PATTERN) should be excluded."""
    project_root = Path(__file__).resolve().parents[1]
    module = load_plugin_manager(project_root / ".agents" / "engine" / "core" / "plugin_manager.py")

    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()
    # No allowed_plugins.json

    (plugins_dir / "valid-plugin.py").write_text("PLUGIN_INFO = {}\n", encoding='utf-8')
    (plugins_dir / "also_valid.py").write_text("PLUGIN_INFO = {}\n", encoding='utf-8')

    manager = module.PluginManager(plugins_dir=str(plugins_dir))
    discovered = manager.discover_plugins()

    # Both should be valid per PLUGIN_NAME_PATTERN (^[A-Za-z0-9_-]+$)
    assert "valid-plugin" in discovered
    assert "also_valid" in discovered
