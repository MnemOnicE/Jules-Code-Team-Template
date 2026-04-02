from unittest.mock import patch, MagicMock
from init_project import update_file

def test_update_file_success(tmp_path):
    """Test successful file update with search and replace."""
    d = tmp_path / "subdir"
    d.mkdir()
    f = d / "test.txt"
    f.write_text("Hello World\nThis is a test.")

    update_file(str(f), r"World", "Jules")

    assert f.read_text() == "Hello Jules\nThis is a test."

def test_update_file_no_file():
    """Test that the function handles non-existent files gracefully."""
    # Should not raise an exception
    update_file("non_existent_file.txt", r"foo", "bar")

def test_update_file_no_match(tmp_path):
    """Test that file content remains unchanged if no match is found."""
    f = tmp_path / "test.txt"
    f.write_text("No match here.")

    update_file(str(f), r"missing", "found")

    assert f.read_text() == "No match here."

def test_update_file_multiline(tmp_path):
    """Test that re.MULTILINE flag works correctly."""
    f = tmp_path / "test.txt"
    content = "Line 1\nLine 2\nLine 3"
    f.write_text(content)

    # ^ matches start of line with MULTILINE
    update_file(str(f), r"^Line 2$", "Modified")

    assert f.read_text() == "Line 1\nModified\nLine 3"

def test_update_file_regex_groups(tmp_path):
    """Test that regex groups can be used in the replacement."""
    f = tmp_path / "test.txt"
    f.write_text("version: 1.0.0")

    update_file(str(f), r"version: (\d+\.\d+\.\d+)", r"stable: \1")

    assert f.read_text() == "stable: 1.0.0"
