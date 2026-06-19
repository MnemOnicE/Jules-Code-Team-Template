import sys
import os
import pytest
from unittest import mock

scripts_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "template_source", "scripts"))
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

from generate_city_metrics import generate_city_metrics, get_complexity

def test_generate_city_metrics_happy_path(tmp_path):
    file1 = tmp_path / "test1.py"
    file1.write_text("print('hello')\nprint('world')\n")

    file2 = tmp_path / "test2.js"
    file2.write_text("console.log('hello');\n")

    file3 = tmp_path / "test3.txt"
    file3.write_text("Some text")

    with mock.patch("generate_city_metrics.count_lines", return_value=10), \
         mock.patch("generate_city_metrics.get_complexity", return_value=2):

        metrics = generate_city_metrics(str(tmp_path))

        assert metrics["name"] == "CodeCity"
        assert len(metrics["children"]) == 2

        filenames = [c["name"] for c in metrics["children"]]
        assert "test1.py" in filenames
        assert "test2.js" in filenames
        assert "test3.txt" not in filenames

        for child in metrics["children"]:
            assert child["loc"] == 10
            assert child["complexity"] == 2

def test_generate_city_metrics_skips_hidden_and_build_dirs(tmp_path):
    hidden_dir = tmp_path / ".hidden"
    hidden_dir.mkdir()
    hidden_file = hidden_dir / "test.py"
    hidden_file.write_text("print('hidden')\n")

    node_modules = tmp_path / "node_modules"
    node_modules.mkdir()
    nm_file = node_modules / "test.js"
    nm_file.write_text("console.log('nm');\n")

    pycache = tmp_path / "__pycache__"
    pycache.mkdir()
    pc_file = pycache / "test.py"
    pc_file.write_text("print('pc')\n")

    valid_file = tmp_path / "valid.py"
    valid_file.write_text("print('valid')\n")

    with mock.patch("generate_city_metrics.count_lines", return_value=5), \
         mock.patch("generate_city_metrics.get_complexity", return_value=1):

        metrics = generate_city_metrics(str(tmp_path))

        assert len(metrics["children"]) == 1
        assert metrics["children"][0]["name"] == "valid.py"

def test_generate_city_metrics_handles_exceptions(tmp_path):
    file1 = tmp_path / "error.py"
    file1.write_text("print('error')\n")

    file2 = tmp_path / "valid.py"
    file2.write_text("print('valid')\n")

    def mock_count_lines(filepath):
        if "error.py" in str(filepath):
            raise ValueError("Test error")
        return 5

    with mock.patch("generate_city_metrics.count_lines", side_effect=mock_count_lines), \
         mock.patch("generate_city_metrics.get_complexity", return_value=1):

        metrics = generate_city_metrics(str(tmp_path))

        assert len(metrics["children"]) == 1
        assert metrics["children"][0]["name"] == "valid.py"


def test_get_complexity_handles_exceptions():
    # Mock lizard explicitly since it might be None if not installed
    lizard_mock = mock.MagicMock()
    lizard_mock.analyze_file.side_effect = Exception("Test error")

    with mock.patch("generate_city_metrics.lizard", lizard_mock):
        complexity = get_complexity("test.py")
        assert complexity == 1
