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
    # Should not raise exception
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
