import os
import sys
from pathlib import Path

test_scripts_path = Path(__file__).resolve().parents[1] / "template_source" / "scripts"
sys.path.insert(0, str(test_scripts_path))

import path_utils


def test_get_agents_dir_prefers_root_dot_agents(tmp_path):
    root = tmp_path
    (root / ".agents").mkdir()
    (root / "template_source" / ".agents").mkdir(parents=True)

    resolved = path_utils.get_agents_dir(str(root))
    assert resolved == str(root / ".agents")


def test_get_agents_dir_falls_back_to_template_source(tmp_path):
    root = tmp_path
    (root / "template_source" / ".agents").mkdir(parents=True)

    resolved = path_utils.get_agents_dir(str(root))
    assert resolved == str(root / "template_source" / ".agents")


def test_get_tech_stack_path_returns_expected_file(tmp_path):
    root = tmp_path
    agents_dir = root / ".agents"
    (agents_dir / "config").mkdir(parents=True)
    expected = agents_dir / "config" / "TECH_STACK.md"
    expected.write_text('# - python', encoding='utf-8')

    result = path_utils.get_tech_stack_path(str(root))
    assert result == str(expected)


def test_get_repo_root_finds_git(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    (root / ".git").mkdir()

    assert path_utils.get_repo_root(str(root)) == str(root)


def test_get_repo_root_finds_agents(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    (root / ".agents").mkdir()

    assert path_utils.get_repo_root(str(root)) == str(root)


def test_get_repo_root_finds_template_source_agents(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "template_source" / ".agents").mkdir(parents=True)

    assert path_utils.get_repo_root(str(root)) == str(root)


def test_get_repo_root_traverses_up(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    (root / ".git").mkdir()
    nested = root / "a" / "b" / "c"
    nested.mkdir(parents=True)

    assert path_utils.get_repo_root(str(nested)) == str(root)


def test_get_repo_root_no_indicator(tmp_path):
    # If no indicator is found up to the root, it should return the resolved start_path
    # We use a path that definitely won't have .git or .agents in its parents
    path = tmp_path / "some" / "path"
    path.mkdir(parents=True)

    assert path_utils.get_repo_root(str(path)) == str(path.resolve())


def test_get_repo_root_default_cwd(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    root.mkdir()
    (root / ".git").mkdir()

    monkeypatch.chdir(root)
    # When start_path is None, it should use os.getcwd() which is now 'root'
    assert path_utils.get_repo_root() == str(root.resolve())
