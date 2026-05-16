import os
import sys
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add scripts directory to path to import smart_ingest
scripts_path = Path(__file__).resolve().parents[1] / "template_source" / "scripts"
sys.path.insert(0, str(scripts_path))

import smart_ingest


def test_get_commit_count_success(monkeypatch):
    def mock_run(*args, **kwargs):
        mock_result = MagicMock()
        mock_result.stdout = "42\n"
        return mock_result

    monkeypatch.setattr(subprocess, "run", mock_run)
    assert smart_ingest.get_commit_count() == 42


def test_get_commit_count_error(monkeypatch, capsys):
    def mock_run(*args, **kwargs):
        raise subprocess.CalledProcessError(1, ["git"])

    monkeypatch.setattr(subprocess, "run", mock_run)
    assert smart_ingest.get_commit_count() == 0
    captured = capsys.readouterr()
    assert "Error: Not a git repository or no commits found." in captured.out


def test_run_ingest_full(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    def mock_run(*args, **kwargs):
        filepath = args[0][3]
        Path(filepath).write_text("dummy digest content")
        return MagicMock()

    monkeypatch.setattr(subprocess, "run", mock_run)

    smart_ingest.run_ingest(is_delta=False)

    ingests_dir = tmp_path / smart_ingest.INGEST_DIR
    assert ingests_dir.exists()

    digests = list(ingests_dir.glob("digest_*.md"))
    assert len(digests) == 1


def test_run_ingest_delta(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    (tmp_path / "test.py").write_text("print('hello')")

    def mock_run(*args, **kwargs):
        mock_result = MagicMock()
        mock_result.stdout = "diff content"
        return mock_result

    monkeypatch.setattr(subprocess, "run", mock_run)

    smart_ingest.run_ingest(is_delta=True)

    ingests_dir = tmp_path / smart_ingest.INGEST_DIR
    assert ingests_dir.exists()

    deltas = list(ingests_dir.glob("delta_*.md"))
    assert len(deltas) == 1

    content = deltas[0].read_text()
    assert "# DELTA INGEST:" in content
    assert "test.py" in content
    assert "diff content" in content


def test_prune_ingests_keeps_last_three_digests(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    ingests_dir = tmp_path / smart_ingest.INGEST_DIR
    ingests_dir.mkdir()

    # Create 5 mock digests
    for i in range(5):
        (ingests_dir / f"digest_2024010{i}_120000.md").touch()

    smart_ingest.prune_ingests()

    remaining = list(ingests_dir.glob("digest_*.md"))
    assert len(remaining) == 3
    # Should keep the newest ones (indices 2, 3, 4)
    assert not (ingests_dir / "digest_20240100_120000.md").exists()
    assert not (ingests_dir / "digest_20240101_120000.md").exists()
    assert (ingests_dir / "digest_20240102_120000.md").exists()


def test_prune_ingests_keeps_last_one_delta(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    ingests_dir = tmp_path / smart_ingest.INGEST_DIR
    ingests_dir.mkdir()

    # Create 3 mock deltas
    for i in range(3):
        (ingests_dir / f"delta_2024010{i}_120000.md").touch()

    smart_ingest.prune_ingests()

    remaining = list(ingests_dir.glob("delta_*.md"))
    assert len(remaining) == 1
    # Should keep the newest one (index 2)
    assert not (ingests_dir / "delta_20240100_120000.md").exists()
    assert not (ingests_dir / "delta_20240101_120000.md").exists()
    assert (ingests_dir / "delta_20240102_120000.md").exists()


@patch('smart_ingest.shutil.which')
def test_main_no_gitingest(mock_which, capsys):
    mock_which.return_value = None

    try:
        smart_ingest.main()
    except SystemExit as e:
        assert e.code == 1

    captured = capsys.readouterr()
    assert "CRITICAL: `gitingest` not found" in captured.out


@patch('smart_ingest.shutil.which')
@patch('smart_ingest.get_commit_count')
@patch('smart_ingest.run_ingest')
@patch('smart_ingest.glob.glob')
@patch('smart_ingest.os.path.exists')
def test_main_force_ingest(mock_exists, mock_glob, mock_run_ingest, mock_get_commit_count, mock_which, monkeypatch):
    mock_which.return_value = "/usr/bin/gitingest"
    mock_get_commit_count.return_value = 1  # Not divisible by 5
    mock_exists.return_value = True
    mock_glob.return_value = ["digest_existing.md"] # Not empty

    monkeypatch.setattr(sys, "argv", ["smart_ingest.py", "--force"])

    smart_ingest.main()

    mock_run_ingest.assert_called_once_with(is_delta=False)
