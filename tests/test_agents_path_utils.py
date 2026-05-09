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


def test_get_session_json_path_returns_expected_file(tmp_path):
    root = tmp_path
    agents_dir = root / ".agents"
    (agents_dir / "memory").mkdir(parents=True)
    expected = agents_dir / "memory" / "session.json"
    expected.write_text('[]', encoding='utf-8')

    result = path_utils.get_session_json_path(str(root))
    assert result == str(expected)


def test_get_tech_stack_path_returns_expected_file(tmp_path):
    root = tmp_path
    agents_dir = root / ".agents"
    (agents_dir / "config").mkdir(parents=True)
    expected = agents_dir / "config" / "TECH_STACK.md"
    expected.write_text('# - python', encoding='utf-8')

    result = path_utils.get_tech_stack_path(str(root))
    assert result == str(expected)
