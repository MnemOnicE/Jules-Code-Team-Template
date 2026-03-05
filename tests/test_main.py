# Jules Code Team Template
# Copyright (C) 2026  MnemOnicE

import pytest
from src.main import generate_mock_graph
from src.core.bus import NexusBus

def test_generate_mock_graph_structure():
    """Test that generate_mock_graph returns a dictionary with the correct structure."""
    task = "Test task"
    graph = generate_mock_graph(task)

    assert isinstance(graph, dict)
    assert "graph_id" in graph
    assert "intent_glyph" in graph
    assert "entry_point" in graph
    assert "nodes" in graph
    assert "context_delta" in graph
    assert graph["intent_glyph"] == "🤖"

def test_generate_mock_graph_task_injection():
    """Test that the task description is correctly injected into the graph."""
    task = "Find the meaning of life"
    graph = generate_mock_graph(task)

    # Check node_2 which should have the task
    node_2 = graph["nodes"].get("node_2")
    assert node_2 is not None
    assert node_2["action"] == "run_tool"
    assert node_2["params"]["tool"] == "plan_decomposition"
    assert node_2["params"]["args"]["task"] == task

def test_generate_mock_graph_validity():
    """Test that the generated graph is valid according to the schema."""
    bus = NexusBus()
    task = "Validate me"
    graph = generate_mock_graph(task)

    # NexusBus.validate_graph raises ValidationError if invalid
    # It returns True or None on success based on implementation
    result = bus.validate_graph(graph)
    assert result is not False

def test_generate_mock_graph_unique_ids():
    """Test that consecutive calls generate unique graph IDs."""
    graph1 = generate_mock_graph("Task 1")
    graph2 = generate_mock_graph("Task 2")

    assert graph1["graph_id"] != graph2["graph_id"]
