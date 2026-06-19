import sys
import os
import pytest

# Add the scripts directory to sys.path to import the module
scripts_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "template_source", "scripts")
)
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

from validate_stack import normalize_name, parse_tech_stack, PACKAGE_MAPPING


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


def test_parse_tech_stack_missing_file(capsys, tmp_path):
    """Test that missing tech stack file returns empty set and prints a warning."""
    # Ensure the file definitely does not exist
    missing_file = tmp_path / "nonexistent.md"

    result = parse_tech_stack(str(missing_file))

    assert result == set()
    captured = capsys.readouterr()
    assert "Warning" in captured.out
    assert "not found. Skipping stack validation." in captured.out


def test_parse_tech_stack_valid_file(tmp_path):
    """Test reading a tech stack file with various line formats."""
    # Create a temporary file with mock contents
    tech_stack_content = """
# - Vue.js
# - FastAPI
# This is a comment, not a package
- Python
# - Pillow
# -
# - invalid!name
"""
    tech_stack_file = tmp_path / "TECH_STACK.md"
    tech_stack_file.write_text(tech_stack_content, encoding="utf-8")

    result = parse_tech_stack(str(tech_stack_file))

    # Expected:
    # "Vue.js" -> lower "vue.js" -> mapping "vue"
    # "FastAPI" -> lower "fastapi" -> normalized "fastapi"
    # "Pillow" -> lower "pillow" -> mapping "PIL"
    # "invalid!name" -> lower -> stripped -> "invalidname"
    assert result == {"vue", "fastapi", "PIL", "invalidname"}


def test_parse_tech_stack_with_notes(tmp_path):
    """Test that parenthetical notes are correctly stripped from tech stack names."""
    # Create a temporary file with mock contents containing notes
    tech_stack_content = """
# - Python 3.10 (Backend)
# - React (Frontend framework)
# - scikit-learn (ML Library)
# - SomeLib(with space issue)
"""
    tech_stack_file = tmp_path / "TECH_STACK.md"
    tech_stack_file.write_text(tech_stack_content, encoding="utf-8")

    result = parse_tech_stack(str(tech_stack_file))

    # Expected:
    # "Python 3.10 (Backend)" -> strip note -> "Python 3.10" -> "python"
    # "React (Frontend framework)" -> strip note -> "React" -> "react"
    # "scikit-learn (ML Library)" -> strip note -> "scikit-learn" -> mapping "sklearn"
    # "SomeLib(with space issue)" -> strip note -> "SomeLib" -> "somelib"
    assert result == {"python", "react", "sklearn", "somelib"}
