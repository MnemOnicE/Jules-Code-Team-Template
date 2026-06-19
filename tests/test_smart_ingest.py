import subprocess
from unittest.mock import patch, MagicMock
from template_source.scripts.smart_ingest import get_commit_count

def test_get_commit_count_success():
    """Test that get_commit_count returns the correct integer on successful subprocess execution."""
    mock_result = MagicMock()
    mock_result.stdout = "42\n"

    with patch("template_source.scripts.smart_ingest.subprocess.run", return_value=mock_result) as mock_run:
        count = get_commit_count()

        mock_run.assert_called_once_with(
            ["git", "rev-list", "--count", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        assert count == 42

def test_get_commit_count_failure():
    """Test that get_commit_count returns 0 when subprocess raises CalledProcessError."""
    with patch("template_source.scripts.smart_ingest.subprocess.run", side_effect=subprocess.CalledProcessError(1, "git")) as mock_run:
        count = get_commit_count()

        mock_run.assert_called_once_with(
            ["git", "rev-list", "--count", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        assert count == 0
