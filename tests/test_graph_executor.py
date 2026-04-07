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
import jsonschema
from unittest.mock import MagicMock
from core.tools.graph_executor import GraphExecutor, SecurityError, MaxStepsExceededError

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

def test_dispatch_action_shizuku_active_injects_use_root(graph_executor):
    """Test that use_root=True is injected when shizuku_active is True in context."""
    node = {
        "action": "run_tool",
        "params": {
            "tool": "test_tool",
            "args": {"arg1": "val1"}
        }
    }
    context = {"shizuku_active": True}

    graph_executor.registry.invoke = MagicMock(return_value={"status": "success"})

    graph_executor._dispatch_action(node, context)

    graph_executor.registry.invoke.assert_called_once_with(
        "test_tool",
        arg1="val1",
        use_root=True
    )

def test_dispatch_action_shizuku_inactive_no_injection(graph_executor):
    """Test that use_root is NOT injected when shizuku_active is False or missing."""
    node = {
        "action": "run_tool",
        "params": {
            "tool": "test_tool",
            "args": {"arg1": "val1"}
        }
    }

    graph_executor.registry.invoke = MagicMock(return_value={"status": "success"})

    # Case: False
    graph_executor._dispatch_action(node, {"shizuku_active": False})
    graph_executor.registry.invoke.assert_called_with("test_tool", arg1="val1")

    # Case: Missing
    graph_executor.registry.invoke.reset_mock()
    graph_executor._dispatch_action(node, {})
    graph_executor.registry.invoke.assert_called_with("test_tool", arg1="val1")

def test_dispatch_action_preserves_existing_args(graph_executor):
    """Test that existing arguments are preserved when shizuku_active is True."""
    node = {
        "action": "run_tool",
        "params": {
            "tool": "test_tool",
            "args": {"other": "value"}
        }
    }
    context = {"shizuku_active": True}
    graph_executor.registry.invoke = MagicMock(return_value={"status": "success"})

    graph_executor._dispatch_action(node, context)

    graph_executor.registry.invoke.assert_called_once_with(
        "test_tool",
        other="value",
        use_root=True
    )

def test_dispatch_action_shizuku_injection_no_side_effect(graph_executor):
    """
    Test that _dispatch_action does NOT modify the input node's args.
    It should use a copy for injection.
    """
    node = {
        "action": "run_tool",
        "params": {
            "tool": "test_tool",
            "args": {"arg1": "val1"}
        }
    }
    context = {"shizuku_active": True}
    graph_executor.registry.invoke = MagicMock(return_value={"status": "success"})

    graph_executor._dispatch_action(node, context)

    # Verify that the original node was NOT modified
    assert "use_root" not in node["params"]["args"]


def test_execute_exception_handling(graph_executor, caplog):
    """Test that exceptions during node execution are caught and logged critically."""
    graph = {
        "intent_glyph": "🧪",
        "entry_point": "node1",
        "nodes": {
            "node1": {
                "action": "run_tool",
                "next": "node2"
            },
            "node2": {
                "action": "run_tool",
                "next": "END"
            }
        }
    }

    # Mock _dispatch_action to raise an exception
    graph_executor._dispatch_action = MagicMock(side_effect=RuntimeError("Simulated Crash"))

    # Mock validate_integrity to avoid unnecessary checks
    graph_executor.validate_integrity = MagicMock()

    # Execute
    graph_executor.execute(graph)

    # Verify execution stopped after the first node (break)
    assert graph_executor._dispatch_action.call_count == 1

    # Verify the exception was logged as CRITICAL
    critical_logs = [record for record in caplog.records if record.levelname == "CRITICAL"]
    assert len(critical_logs) == 1
    assert "Graph Crash: Simulated Crash" in critical_logs[0].message

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
    graph_executor.bus.validate_graph.assert_called_once_with(graph)
    graph_executor.validate_integrity.assert_called_once_with(graph)
    assert graph_executor._dispatch_action.call_count == 2

    # Verify calls to _dispatch_action were made with correct nodes
    actual_nodes = [call.args[0] for call in graph_executor._dispatch_action.call_args_list]
    assert actual_nodes == [graph["nodes"]["node1"], graph["nodes"]["node2"]]

def test_execute_validation_failure(graph_executor):
    """Test that execution stops if structural validation fails."""
    graph = {"nodes": {}}

    # Mock validation failure
    graph_executor.bus.validate_graph.side_effect = jsonschema.ValidationError("Invalid graph")

    # Execute should raise ValidationError
    with pytest.raises(jsonschema.ValidationError):
        graph_executor.execute(graph)

def test_execute_missing_node(graph_executor, caplog):
    """Test that execution handles missing nodes gracefully."""
    graph = {
        "intent_glyph": "🧪",
        "entry_point": "node1",
        "nodes": {
            "node1": {
                "action": "run_tool",
                "next": "missing_node"
            }
        }
    }

    graph_executor.validate_integrity = MagicMock()
    graph_executor._dispatch_action = MagicMock(return_value={"status": "success"})

    with caplog.at_level("ERROR"):
        graph_executor.execute(graph)

    assert "[ERROR] Node 'missing_node' not found in graph." in caplog.text

def test_execute_traversal_logic(graph_executor):
    """Test that on_success takes precedence over next."""
    graph = {
        "intent_glyph": "🧪",
        "entry_point": "node1",
        "nodes": {
            "node1": {
                "action": "run_tool",
                "on_success": "success_node",
                "next": "next_node"
            },
            "success_node": {"action": "terminate"},
            "next_node": {"action": "terminate"}
        }
    }

    graph_executor.validate_integrity = MagicMock()
    graph_executor._dispatch_action = MagicMock(return_value={"status": "success"})

    graph_executor.execute(graph)

    # Should visit node1 then success_node
    actual_nodes = [call.args[0] for call in graph_executor._dispatch_action.call_args_list]
    assert actual_nodes == [graph["nodes"]["node1"], graph["nodes"]["success_node"]]

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

    assert "[EXECUTING] Node node1: test_action" in caplog.text

def test_validate_integrity_shield_with_scan(graph_executor):
    """Test validation passes when security_scan precedes a privileged tool."""
    graph = {
        "intent_glyph": "🛡️",
        "entry_point": "scan",
        "nodes": {
            "scan": {"action": "security_scan", "next": "start"},
            "start": {"action": "run_tool", "params": {"tool": "execute_command"}}
        }
    }
    # Should not raise exception
    graph_executor.validate_integrity(graph)

def test_validate_integrity_shield_missing_scan(graph_executor):
    """Test validation raises SecurityError when a privileged tool is missing a prior security_scan."""
    graph = {
        "intent_glyph": "🛡️",
        "entry_point": "start",
        "nodes": {
            "start": {"action": "run_tool", "params": {"tool": "execute_command"}}
        }
    }
    with pytest.raises(SecurityError, match="Unverified path to privileged tool 'execute_command' detected. Halting."):
        graph_executor.validate_integrity(graph)

def test_validate_integrity_empty_glyph(graph_executor):
    """Test validation passes when intent_glyph is empty, provided no privileged tool is run without scan."""
    graph = {
        "intent_glyph": "",
        "entry_point": "start",
        "nodes": {"start": {"action": "run_tool", "params": {"tool": "read_file"}}}
    }
    # Should not raise exception
    graph_executor.validate_integrity(graph)

def test_validate_integrity_missing_glyph_key(graph_executor):
    """Test validation passes when intent_glyph key is missing (defaults to empty string)."""
    graph = {
        "entry_point": "start",
        "nodes": {"start": {"action": "run_tool", "params": {"tool": "read_file"}}}
    }
    # Should not raise exception
    graph_executor.validate_integrity(graph)

def test_validate_integrity_none_glyph(graph_executor):
    """Test validation handles explicit None for intent_glyph gracefully (treats as empty)."""
    graph = {
        "intent_glyph": None,
        "entry_point": "start",
        "nodes": {"start": {"action": "run_tool", "params": {"tool": "read_file"}}}
    }
    # Should not raise exception
    graph_executor.validate_integrity(graph)

def test_validate_integrity_loose_check(graph_executor):
    """
    Test that an orphaned security_scan does not bypass the check for a privileged tool.
    """
    graph = {
        "intent_glyph": "🛡️",
        "entry_point": "start",
        "nodes": {
            "start": {"action": "run_tool", "params": {"tool": "execute_command"}},
            "fake_scan": {"action": "security_scan"}
        }
    }
    # Should raise exception because scan is not in path
    with pytest.raises(SecurityError, match="Unverified path to privileged tool"):
        graph_executor.validate_integrity(graph)

def test_validate_integrity_multiple_shields(graph_executor):
    """Test validation handles multiple shields correctly (it shouldn't matter anymore)."""
    graph = {
        "intent_glyph": "🛡️🛡️",
        "entry_point": "scan",
        "nodes": {
            "scan": {"action": "security_scan", "next": "start"},
            "start": {"action": "run_tool", "params": {"tool": "execute_command"}}
        }
    }
    # Should not raise exception
    graph_executor.validate_integrity(graph)

def test_validate_integrity_failure_path_bypass(graph_executor):
    """Test that an attacker cannot bypass the scan by using an on_failure edge."""
    graph = {
        "intent_glyph": "🧪",
        "entry_point": "node1",
        "nodes": {
            "node1": {
                "action": "run_tool",
                "params": {"tool": "read_file"},
                "on_failure": "hack_node"
            },
            "hack_node": {
                "action": "run_tool",
                "params": {"tool": "modify_context"}
            }
        }
    }
    with pytest.raises(SecurityError, match="Unverified path to privileged tool 'modify_context' detected"):
        graph_executor.validate_integrity(graph)

def test_execute_max_steps_exceeded(graph_executor, caplog):
    """Test that cyclic graphs are terminated when MAX_STEPS is exceeded."""
    graph = {
        "intent_glyph": "🧪",
        "entry_point": "node1",
        "nodes": {
            "node1": {
                "action": "test_action",
                "next": "node2"
            },
            "node2": {
                "action": "test_action",
                "next": "node1"
            }
        }
    }

    # Temporarily set a small MAX_STEPS for the test
    original_max = graph_executor.MAX_STEPS
    graph_executor.MAX_STEPS = 5

    graph_executor.validate_integrity = MagicMock()
    graph_executor._dispatch_action = MagicMock(return_value={"status": "success"})

    try:
        with pytest.raises(MaxStepsExceededError):
            graph_executor.execute(graph)
    finally:
        graph_executor.MAX_STEPS = original_max

    # Verify it stopped at 5 + 1 steps (the check is step_count > MAX_STEPS)
    # Actually it will execute node1, node2, node1, node2, node1.
    # step_count will be 1, 2, 3, 4, 5.
    # When step_count becomes 6, it hits the limit.
    assert graph_executor._dispatch_action.call_count == 5

    # Verify error was logged
    assert f"Max steps (5) exceeded. Potential infinite loop." in caplog.text

def test_execute_retry_same_node(graph_executor, caplog):
    """Test that the executor retries the same node when retry_on_fail is True and no on_failure node is present."""
    graph = {
        "intent_glyph": "🧪",
        "entry_point": "node1",
        "context_delta": {"retry_on_fail": True},
        "nodes": {
            "node1": {
                "action": "run_tool",
                "next": "END"
            }
        }
    }

    graph_executor.validate_integrity = MagicMock()
    # Mock tool to fail
    graph_executor._dispatch_action = MagicMock(return_value={"status": "error"})

    with caplog.at_level("WARNING"):
        graph_executor.execute(graph)

    # Initial execution + 3 retries = 4 calls
    assert graph_executor._dispatch_action.call_count == 4
    assert "Triggering Self-Correction Loop..." in caplog.text
    assert caplog.text.count("Triggering Self-Correction Loop...") == 3
    assert "Max retries exceeded. Aborting." in caplog.text

def test_execute_retry_with_repair_node(graph_executor, caplog):
    """Test that the executor transitions to the on_failure node and increments retry_count."""
    graph = {
        "intent_glyph": "🧪",
        "entry_point": "node1",
        "context_delta": {"retry_on_fail": True},
        "nodes": {
            "node1": {
                "action": "run_tool",
                "on_failure": "repair_node",
                "next": "END"
            },
            "repair_node": {
                "action": "run_tool",
                "next": "node1"
            }
        }
    }

    graph_executor.validate_integrity = MagicMock()
    # First call to node1 fails, repair_node succeeds, second call to node1 succeeds
    graph_executor._dispatch_action = MagicMock(side_effect=[
        {"status": "error"},   # node1 (fail)
        {"status": "success"}, # repair_node (success)
        {"status": "success"}  # node1 (success)
    ])

    graph_executor.execute(graph)

    assert graph_executor._dispatch_action.call_count == 3
    assert "Triggering Self-Correction Loop..." in caplog.text
    # Verify context was updated
    context_passed_to_last_call = graph_executor._dispatch_action.call_args_list[-1].args[1]
    assert context_passed_to_last_call["retry_count"] == 1

def test_execute_max_retries_exceeded(graph_executor, caplog):
    """Test that the executor stops after max retries."""
    graph = {
        "intent_glyph": "🧪",
        "entry_point": "node1",
        "context_delta": {"retry_on_fail": True},
        "nodes": {
            "node1": {
                "action": "run_tool",
                "next": "END"
            }
        }
    }

    graph_executor.validate_integrity = MagicMock()
    graph_executor._dispatch_action = MagicMock(return_value={"status": "error"})

    with caplog.at_level("ERROR"):
        graph_executor.execute(graph)

    assert graph_executor._dispatch_action.call_count == 4 # 1st try + 3 retries
    assert "Max retries exceeded. Aborting." in caplog.text

def test_execute_failure_without_retry(graph_executor, caplog):
    """Test that the executor follows on_failure immediately if retry_on_fail is False."""
    graph = {
        "intent_glyph": "🧪",
        "entry_point": "node1",
        "context_delta": {"retry_on_fail": False},
        "nodes": {
            "node1": {
                "action": "run_tool",
                "on_failure": "fail_node",
                "next": "END"
            },
            "fail_node": {
                "action": "run_tool",
                "next": "END"
            }
        }
    }

    graph_executor.validate_integrity = MagicMock()
    graph_executor._dispatch_action = MagicMock(return_value={"status": "error"})

    graph_executor.execute(graph)

    # node1 fails, then fail_node (even if it also fails, it will just try to move to next/on_failure)
    # Wait, the code says:
    # else:
    #     current_node_id = repair_node
    #     if context.get("retry_on_fail"):
    #          self.logger.error("Max retries exceeded. Aborting.")
    #          break
    # If retry_on_fail is False, it just sets current_node_id = repair_node and continues.
    assert graph_executor._dispatch_action.call_count == 2
    assert "Triggering Self-Correction Loop..." not in caplog.text
