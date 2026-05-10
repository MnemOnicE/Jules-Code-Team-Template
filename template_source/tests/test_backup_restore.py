import io
import tarfile
from pathlib import Path
import importlib.util


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_create_backup_and_list(tmp_path, monkeypatch):
    project = tmp_path / "repo"
    project.mkdir()
    monkeypatch.chdir(project)

    agents_dir = project / ".agents"
    (agents_dir / "config").mkdir(parents=True)
    (agents_dir / "memory").mkdir(parents=True)
    (agents_dir / "rules").mkdir(parents=True)
    (project / "session.json").write_text('[]', encoding='utf-8')
    (project / "AI_MEMORY.md").write_text("memory", encoding='utf-8')

    repo_root = Path(__file__).resolve().parents[1]
    module = load_module(repo_root / "scripts" / "backup_restore.py", "backup_restore")
    assert module.create_backup()

    backups = list(project.glob('agents_backup_*.tar.gz'))
    assert backups, "Backup archive was not created"

    module.list_backups()
    assert backups[0].exists()


def test_restore_rejects_path_traversal(tmp_path, monkeypatch):
    project = tmp_path / "repo"
    project.mkdir()
    monkeypatch.chdir(project)

    malicious_tar = project / "malicious.tar.gz"
    with tarfile.open(malicious_tar, "w:gz") as tar:
        info = tarfile.TarInfo(name="../evil.txt")
        info.size = len(b"bad")
        tar.addfile(info, io.BytesIO(b"bad"))

    repo_root = Path(__file__).resolve().parents[1]
    module = load_module(repo_root / "scripts" / "backup_restore.py", "backup_restore")
    assert not module.restore_backup(str(malicious_tar), force=True)
    assert not (project.parent / "evil.txt").exists()


# --- Tests for PR changes ---

def test_safe_extract_raises_exception_not_valueerror_on_path_traversal(tmp_path):
    """_safe_extract should raise Exception (not ValueError) on path traversal."""
    repo_root = Path(__file__).resolve().parents[1]
    module = load_module(repo_root / "scripts" / "backup_restore.py", "backup_restore")

    malicious_tar_path = tmp_path / "traversal.tar.gz"
    with tarfile.open(malicious_tar_path, "w:gz") as tar:
        info = tarfile.TarInfo(name="../outside.txt")
        info.size = len(b"bad")
        tar.addfile(info, io.BytesIO(b"bad"))

    with tarfile.open(malicious_tar_path, "r:gz") as tar:
        try:
            module._safe_extract(tar, str(tmp_path))
            assert False, "Expected an exception to be raised"
        except Exception as e:
            # Must be Exception (or subclass), not specifically ValueError
            assert type(e) is Exception, f"Expected Exception, got {type(e).__name__}"
            assert "Unsafe path" in str(e)


def test_safe_extract_raises_exception_not_valueerror_on_symlink(tmp_path):
    """_safe_extract should raise Exception (not ValueError) on symlink member."""
    repo_root = Path(__file__).resolve().parents[1]
    module = load_module(repo_root / "scripts" / "backup_restore.py", "backup_restore")

    symlink_tar_path = tmp_path / "symlink.tar.gz"
    with tarfile.open(symlink_tar_path, "w:gz") as tar:
        info = tarfile.TarInfo(name="link_file")
        info.type = tarfile.SYMTYPE
        info.linkname = "/etc/passwd"
        info.size = 0
        tar.addfile(info)

    with tarfile.open(symlink_tar_path, "r:gz") as tar:
        try:
            module._safe_extract(tar, str(tmp_path))
            assert False, "Expected an exception to be raised"
        except Exception as e:
            assert type(e) is Exception, f"Expected Exception, got {type(e).__name__}"
            assert "symlink" in str(e).lower() or "Unsupported" in str(e)


def test_create_backup_backs_up_specific_subdirs_not_entire_agents(tmp_path, monkeypatch):
    """create_backup should back up .agents/config, .agents/memory, .agents/rules — not all of .agents."""
    project = tmp_path / "repo"
    project.mkdir()
    monkeypatch.chdir(project)

    agents_dir = project / ".agents"
    (agents_dir / "config").mkdir(parents=True)
    (agents_dir / "memory").mkdir(parents=True)
    (agents_dir / "rules").mkdir(parents=True)
    # Create a file outside the specific subdirs that should NOT be backed up
    (agents_dir / "extra_dir").mkdir()
    (agents_dir / "extra_dir" / "secret.txt").write_text("should not be backed up", encoding='utf-8')
    (agents_dir / "config" / "brain.md").write_text("config content", encoding='utf-8')
    (project / "session.json").write_text('[]', encoding='utf-8')

    repo_root = Path(__file__).resolve().parents[1]
    module = load_module(repo_root / "scripts" / "backup_restore.py", "backup_restore")
    backup_path = str(project / "test_backup.tar.gz")
    result = module.create_backup(output_path=backup_path)
    assert result is True

    # Inspect what was actually backed up
    with tarfile.open(backup_path, "r:gz") as tar:
        names = tar.getnames()

    # config should be present
    assert any(".agents/config" in n for n in names), f"config not in backup: {names}"
    # The secret extra_dir file should NOT be in backup
    assert not any("extra_dir" in n for n in names), f"extra_dir unexpectedly in backup: {names}"


def test_create_backup_returns_false_when_no_agents_dir(tmp_path, monkeypatch):
    """create_backup should return False when .agents directory does not exist."""
    project = tmp_path / "empty_project"
    project.mkdir()
    monkeypatch.chdir(project)

    repo_root = Path(__file__).resolve().parents[1]
    module = load_module(repo_root / "scripts" / "backup_restore.py", "backup_restore")
    result = module.create_backup(output_path=str(project / "backup.tar.gz"))
    assert result is False


def test_create_backup_no_agents_dir_does_not_create_archive(tmp_path, monkeypatch):
    """create_backup should not create a tar.gz file when .agents doesn't exist."""
    project = tmp_path / "empty_project"
    project.mkdir()
    monkeypatch.chdir(project)

    repo_root = Path(__file__).resolve().parents[1]
    module = load_module(repo_root / "scripts" / "backup_restore.py", "backup_restore")
    output = str(project / "should_not_exist.tar.gz")
    module.create_backup(output_path=output)
    assert not (project / "should_not_exist.tar.gz").exists()
