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
