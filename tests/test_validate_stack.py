import sys
import os
import pytest

# Add the scripts directory to sys.path to import the module
scripts_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "template_source", "scripts"))
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

from validate_stack import normalize_name

def test_normalize_name_basic():
    """Test basic lowercasing and normalization."""
    assert normalize_name("FastAPI") == "fastapi"
    assert normalize_name("Python") == "python"

def test_normalize_name_mapping():
    """Test that items in PACKAGE_MAPPING are correctly handled."""
    # Based on PACKAGE_MAPPING = {"vue.js": "vue", "scikit-learn": "sklearn", "beautifulsoup4": "bs4", "pillow": "PIL"}
    assert normalize_name("Vue.js") == "vue"
    assert normalize_name("scikit-learn") == "sklearn"
    assert normalize_name("BeautifulSoup4") == "bs4"
    assert normalize_name("Pillow") == "PIL"

def test_normalize_name_version_stripping():
    """Test that version numbers are stripped from the name."""
    assert normalize_name("Python 3.10") == "python"
    assert normalize_name("Library 1.2.3") == "library"
    # Note: heuristic requires space before version
    assert normalize_name("SomePkg 2.0-beta") == "somepkg"
    # If no space, it won't strip (according to current regex \s+\d+)
    assert normalize_name("PackageV2") == "packagev2"

def test_normalize_name_special_chars():
    """Test removal of special characters except underscores."""
    assert normalize_name("my-package!") == "mypackage"
    assert normalize_name("complex.name@v1") == "complexnamev1"
    assert normalize_name("my_package") == "my_package"

def test_normalize_name_whitespace():
    """Test handling of whitespace."""
    # Input "  Strip Me  " -> lower "  strip me  " -> no version -> not in mapping
    # -> strip special chars (including spaces) -> "stripme"
    assert normalize_name("  Strip Me  ") == "stripme"
    assert normalize_name("Multiple   Spaces") == "multiplespaces"

def test_normalize_name_edge_cases():
    """Test various edge cases."""
    assert normalize_name("") == ""
    assert normalize_name("!!!") == ""
    assert normalize_name("123") == "123"
    assert normalize_name("already_normalized") == "already_normalized"
