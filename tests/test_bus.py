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
from core.bus import NexusBus

# Determine if jsonschema is a mock (occurs in environments without the library)
# Some tests rely on real schema validation and should be skipped if it's mocked.
JS_IS_MOCKED = isinstance(getattr(jsonschema, "validate", None), MagicMock)

@pytest.fixture
def nexus_bus():
    bus = NexusBus()
    # Reset mock state if it is a mock
    if hasattr(bus.validator, "reset_mock"):
        bus.validator.reset_mock()
        if hasattr(bus.validator.validate, "side_effect"):
            bus.validator.validate.side_effect = None
    return bus

def test_validate_graph_happy_path(nexus_bus):
    """Test validate_graph with a fully valid graph dictionary."""
    valid_graph = {
        "graph_id": "test-uuid-1234",
        "intent_glyph": "🧪",
        "entry_point": "start_node",
        "nodes": {
            "start_node": {
                "action": "run_tool",
                "params": {"tool": "test_tool"},
                "on_success": "end_node"
            },
            "end_node": {
                "action": "terminate"
            }
        }
    }
    assert nexus_bus.validate_graph(valid_graph) is True

@pytest.mark.skipif(JS_IS_MOCKED, reason="Requires real jsonschema for schema validation")
def test_validate_graph_missing_required_fields(nexus_bus):
    """Test that missing required fields raise ValidationError."""
    required_fields = ["graph_id", "intent_glyph", "nodes", "entry_point"]

    base_graph = {
        "graph_id": "test-uuid-1234",
        "intent_glyph": "🧪",
        "entry_point": "node_1",
        "nodes": {"node_1": {"action": "terminate"}}
    }

    for field in required_fields:
        invalid_graph = base_graph.copy()
        del invalid_graph[field]
        with pytest.raises(jsonschema.ValidationError):
            nexus_bus.validate_graph(invalid_graph)

@pytest.mark.skipif(JS_IS_MOCKED, reason="Requires real jsonschema for schema validation")
def test_validate_graph_invalid_types(nexus_bus):
    """Test that invalid data types raise ValidationError."""
    invalid_graph = {
        "graph_id": 12345,  # Should be string
        "intent_glyph": "🧪",
        "entry_point": "node_1",
        "nodes": {"node_1": {"action": "terminate"}}
    }
    with pytest.raises(jsonschema.ValidationError):
        nexus_bus.validate_graph(invalid_graph)

@pytest.mark.skipif(JS_IS_MOCKED, reason="Requires real jsonschema for schema validation")
def test_validate_graph_invalid_node_action(nexus_bus):
    """Test that an invalid node action raises ValidationError."""
    invalid_graph = {
        "graph_id": "test-uuid-1234",
        "intent_glyph": "🧪",
        "entry_point": "node_1",
        "nodes": {
            "node_1": {
                "action": "invalid_action"  # Not in enum
            }
        }
    }
    with pytest.raises(jsonschema.ValidationError):
        nexus_bus.validate_graph(invalid_graph)

@pytest.mark.skipif(JS_IS_MOCKED, reason="Requires real jsonschema for schema validation")
def test_validate_graph_malformed_node(nexus_bus):
    """Test that a node missing the 'action' field raises ValidationError."""
    invalid_graph = {
        "graph_id": "test-uuid-1234",
        "intent_glyph": "🧪",
        "entry_point": "node_1",
        "nodes": {
            "node_1": {
                "params": {}  # Missing 'action'
            }
        }
    }
    with pytest.raises(jsonschema.ValidationError):
        nexus_bus.validate_graph(invalid_graph)

@pytest.mark.skipif(JS_IS_MOCKED, reason="Requires real jsonschema for schema validation")
def test_validate_graph_empty_input(nexus_bus):
    """Test that passing an empty dictionary or None raises ValidationError."""
    # Test empty dict
    with pytest.raises(jsonschema.ValidationError):
        nexus_bus.validate_graph({})

    # Test None
    with pytest.raises(jsonschema.ValidationError):
        nexus_bus.validate_graph(None)

