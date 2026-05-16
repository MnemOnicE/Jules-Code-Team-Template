import pytest
from unittest.mock import patch, MagicMock
import sys

# Import the module to test
import generate_city_metrics

def test_get_complexity_no_lizard():
    """Test get_complexity when lizard is not available."""
    with patch('generate_city_metrics.lizard', None):
        assert generate_city_metrics.get_complexity("some_file.py") == 1

def test_get_complexity_markdown():
    """Test get_complexity explicitly ignores .md files."""
    # Even if lizard is present, it should return 1 for .md
    with patch('generate_city_metrics.lizard', MagicMock()):
        assert generate_city_metrics.get_complexity("README.md") == 1

def test_get_complexity_success_high_ccn():
    """Test get_complexity when lizard analyzes successfully and CCN > 1."""
    mock_lizard = MagicMock()
    mock_analysis = MagicMock()
    mock_analysis.CCN = 5
    mock_lizard.analyze_file.return_value = mock_analysis

    with patch('generate_city_metrics.lizard', mock_lizard):
        assert generate_city_metrics.get_complexity("complex_file.py") == 5
        mock_lizard.analyze_file.assert_called_once_with("complex_file.py")

def test_get_complexity_success_low_ccn():
    """Test get_complexity when lizard analyzes successfully and CCN < 1."""
    mock_lizard = MagicMock()
    mock_analysis = MagicMock()
    mock_analysis.CCN = 0
    mock_lizard.analyze_file.return_value = mock_analysis

    with patch('generate_city_metrics.lizard', mock_lizard):
        assert generate_city_metrics.get_complexity("simple_file.py") == 1
        mock_lizard.analyze_file.assert_called_once_with("simple_file.py")

def test_get_complexity_exception(capsys):
    """Test get_complexity when lizard.analyze_file raises an exception."""
    mock_lizard = MagicMock()
    mock_lizard.analyze_file.side_effect = Exception("Test exception")

    with patch('generate_city_metrics.lizard', mock_lizard):
        # We need to capture stderr to verify the print statement,
        # but the function writes directly to sys.stderr so capsys catches it
        assert generate_city_metrics.get_complexity("error_file.py") == 1
        mock_lizard.analyze_file.assert_called_once_with("error_file.py")

        captured = capsys.readouterr()
        assert "Complexity error for error_file.py: Test exception" in captured.err
