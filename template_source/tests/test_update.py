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
