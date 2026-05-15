import subprocess
from unittest.mock import patch, MagicMock
from smart_ingest import get_commit_count

def test_get_commit_count_success():
    """Test get_commit_count returns correct count on success."""
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.stdout = "10\n"
        mock_run.return_value = mock_result

        count = get_commit_count()

        assert count == 10
        mock_run.assert_called_once_with(
            ["git", "rev-list", "--count", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )

def test_get_commit_count_error(capsys):
    """Test get_commit_count returns 0 and prints error on CalledProcessError."""
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(1, ["git", "rev-list", "--count", "HEAD"])

        count = get_commit_count()

        assert count == 0
        captured = capsys.readouterr()
        assert "Error: Not a git repository or no commits found." in captured.out
