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
