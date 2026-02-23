# Jules Code Team Template
# Copyright (C) 2026  MnemOnicE
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import pytest
from unittest.mock import MagicMock
from src.core.tools.graph_executor import GraphExecutor, SecurityError

@pytest.fixture
def graph_executor():
    mock_bus = MagicMock()
    return GraphExecutor(event_bus=mock_bus)

def test_validate_integrity_no_shield(graph_executor):
    """Test validation passes when intent_glyph does not contain shield."""
    graph = {
        "intent_glyph": "🧪",
        "nodes": {"start": {"action": "run_tool"}}
    }
    # Should not raise exception
    graph_executor.validate_integrity(graph)

def test_execute_happy_path(graph_executor):
    """Test the happy path of graph execution with multiple nodes."""
    graph = {
        "intent_glyph": "🧪",
        "entry_point": "node1",
        "nodes": {
            "node1": {
                "action": "run_tool",
                "params": {"tool": "tool1"},
                "next": "node2"
            },
            "node2": {
                "action": "run_tool",
                "params": {"tool": "tool2"},
                "next": "END"
            }
        }
    }

    # Mock internal methods to isolate control flow
    graph_executor.validate_integrity = MagicMock()
    graph_executor._dispatch_action = MagicMock(return_value={"status": "success"})

    # Execute
    graph_executor.execute(graph)

    # Verify control flow
    graph_executor.validate_integrity.assert_called_once_with(graph)
    assert graph_executor._dispatch_action.call_count == 2

    # Verify calls to _dispatch_action were made with correct nodes
    calls = graph_executor._dispatch_action.call_args_list
    assert calls[0][0][0] == graph["nodes"]["node1"]
    assert calls[1][0][0] == graph["nodes"]["node2"]

def test_execute_with_context_delta(graph_executor):
    """Test that context_delta is correctly passed to the execution loop."""
    context_delta = {"user_id": "123", "debug": True}
    graph = {
        "intent_glyph": "🧪",
        "entry_point": "node1",
        "context_delta": context_delta,
        "nodes": {
            "node1": {
                "action": "run_tool",
                "params": {"tool": "tool1"},
                "next": "END"
            }
        }
    }

    graph_executor._dispatch_action = MagicMock(return_value={"status": "success"})

    # Execute
    graph_executor.execute(graph)

    # Verify context_delta was passed to _dispatch_action
    graph_executor._dispatch_action.assert_called_once_with(
        graph["nodes"]["node1"],
        context_delta
    )

def test_execute_happy_path_logging(graph_executor, caplog):
    """Test that the execution of nodes is logged correctly."""
    graph = {
        "intent_glyph": "🧪",
        "entry_point": "node1",
        "nodes": {
            "node1": {
                "action": "test_action",
                "next": "END"
            }
        }
    }

    graph_executor._dispatch_action = MagicMock(return_value={"status": "success"})

    with caplog.at_level("INFO"):
        graph_executor.execute(graph)

    assert "Executing Node: node1 [test_action]" in caplog.text

def test_validate_integrity_shield_with_scan(graph_executor):
    """Test validation passes when intent_glyph contains shield and security_scan is present."""
    graph = {
        "intent_glyph": "🛡️",
        "nodes": {
            "scan": {"action": "security_scan"},
            "start": {"action": "run_tool"}
        }
    }
    # Should not raise exception
    graph_executor.validate_integrity(graph)

def test_validate_integrity_shield_missing_scan(graph_executor):
    """Test validation raises SecurityError when shield is present but security_scan is missing."""
    graph = {
        "intent_glyph": "🛡️",
        "nodes": {
            "start": {"action": "run_tool"}
        }
    }
    with pytest.raises(SecurityError, match="Graph deviates from Sentinel Intent! Halting."):
        graph_executor.validate_integrity(graph)

def test_validate_integrity_empty_glyph(graph_executor):
    """Test validation passes when intent_glyph is empty."""
    graph = {
        "intent_glyph": "",
        "nodes": {"start": {"action": "run_tool"}}
    }
    # Should not raise exception
    graph_executor.validate_integrity(graph)

def test_validate_integrity_missing_glyph_key(graph_executor):
    """Test validation passes when intent_glyph key is missing (defaults to empty string)."""
    graph = {
        "nodes": {"start": {"action": "run_tool"}}
    }
    # Should not raise exception
    graph_executor.validate_integrity(graph)

def test_validate_integrity_none_glyph(graph_executor):
    """Test validation handles explicit None for intent_glyph gracefully (treats as empty)."""
    graph = {
        "intent_glyph": None,
        "nodes": {"start": {"action": "run_tool"}}
    }
    # Should not raise exception (currently crashes, fix required)
    graph_executor.validate_integrity(graph)

def test_validate_integrity_loose_check(graph_executor):
    """
    Test documents the current loose validation behavior:
    'security_scan' in a value (not action) satisfies the check.
    """
    graph = {
        "intent_glyph": "🛡️",
        "metadata": "security_scan",  # This triggers the check
        "nodes": {"start": {"action": "run_tool"}}
    }
    # Should not raise exception due to str(graph) check
    graph_executor.validate_integrity(graph)

def test_validate_integrity_multiple_shields(graph_executor):
    """Test validation handles multiple shields correctly."""
    graph = {
        "intent_glyph": "🛡️🛡️",
        "nodes": {
            "scan": {"action": "security_scan"},
            "start": {"action": "run_tool"}
        }
    }
    # Should not raise exception
    graph_executor.validate_integrity(graph)
