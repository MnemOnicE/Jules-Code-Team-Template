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


# --- Tests for PR changes ---

def test_get_latest_version_returns_hardcoded_v100():
    """get_latest_version should return the hardcoded placeholder 'v1.0.0' (PR change)."""
    update = load_update_module(Path(__file__).resolve().parents[1] / "scripts" / "update.py")
    result = update.get_latest_version()
    assert result == "v1.0.0"


def test_get_latest_version_never_returns_none():
    """get_latest_version should not return None (placeholder always returns a value)."""
    update = load_update_module(Path(__file__).resolve().parents[1] / "scripts" / "update.py")
    result = update.get_latest_version()
    assert result is not None


def test_get_latest_version_returns_valid_semver():
    """get_latest_version should return a parseable semver string."""
    update = load_update_module(Path(__file__).resolve().parents[1] / "scripts" / "update.py")
    result = update.get_latest_version()
    # Should be parseable by the module's own parse_version
    parsed = update.parse_version(result)
    assert parsed is not None, f"get_latest_version returned non-parseable version: {result}"
