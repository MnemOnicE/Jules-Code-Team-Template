import io
import tarfile
import os
from pathlib import Path
import importlib.util
import pytest

def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

@pytest.fixture
def backup_restore_module():
    repo_root = Path(__file__).resolve().parents[1]
    return load_module(repo_root / "scripts" / "backup_restore.py", "backup_restore")

def test_path_traversal_absolute(tmp_path, backup_restore_module, monkeypatch):
    project = tmp_path / "repo"
    project.mkdir()
    monkeypatch.chdir(project)

    malicious_tar = project / "malicious_abs.tar.gz"
    with tarfile.open(malicious_tar, "w:gz") as tar:
        # Attempt an absolute path traversal
        info = tarfile.TarInfo(name="/tmp/evil_abs.txt")
        info.size = len(b"bad")
        tar.addfile(info, io.BytesIO(b"bad"))

    # The current implementation should catch this via _is_within_directory
    assert not backup_restore_module.restore_backup(str(malicious_tar), force=True)
    assert not os.path.exists("/tmp/evil_abs.txt")

def test_symlink_rejection(tmp_path, backup_restore_module, monkeypatch):
    project = tmp_path / "repo"
    project.mkdir()
    monkeypatch.chdir(project)

    malicious_tar = project / "malicious_sym.tar.gz"
    with tarfile.open(malicious_tar, "w:gz") as tar:
        info = tarfile.TarInfo(name="link")
        info.type = tarfile.SYMTYPE
        info.linkname = "/tmp/some_dir"
        tar.addfile(info)

    # The current implementation should catch this via member.issym()
    assert not backup_restore_module.restore_backup(str(malicious_tar), force=True)

def test_hardlink_rejection(tmp_path, backup_restore_module, monkeypatch):
    project = tmp_path / "repo"
    project.mkdir()
    monkeypatch.chdir(project)

    malicious_tar = project / "malicious_lnk.tar.gz"
    with tarfile.open(malicious_tar, "w:gz") as tar:
        info = tarfile.TarInfo(name="link")
        info.type = tarfile.LNKTYPE
        info.linkname = "/tmp/some_file"
        tar.addfile(info)

    # The current implementation should catch this via member.islnk()
    assert not backup_restore_module.restore_backup(str(malicious_tar), force=True)

def test_safe_extraction_works(tmp_path, backup_restore_module, monkeypatch):
    project = tmp_path / "repo"
    project.mkdir()
    monkeypatch.chdir(project)

    safe_tar = project / "safe.tar.gz"
    with tarfile.open(safe_tar, "w:gz") as tar:
        content = b"safe content"
        info = tarfile.TarInfo(name=".agents/config/settings.yaml")
        info.size = len(content)
        tar.addfile(info, io.BytesIO(content))

    assert backup_restore_module.restore_backup(str(safe_tar), force=True)
    assert (project / ".agents/config/settings.yaml").read_bytes() == content
