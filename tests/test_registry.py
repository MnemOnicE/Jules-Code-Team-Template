import pytest
import threading
import logging
from core.tools.registry import ToolRegistry

@pytest.fixture
def registry():
    """Fixture to provide a fresh ToolRegistry instance for each test."""
    return ToolRegistry()

def test_register_success(registry, caplog):
    """Test registering a valid callable works and logs debug message."""
    def dummy_tool(arg1, arg2):
        return arg1 + arg2

    with caplog.at_level(logging.DEBUG):
        registry.register("dummy_tool", dummy_tool)

    assert "dummy_tool" in registry._tools
    assert registry._tools["dummy_tool"] == dummy_tool
    assert "Registered tool: dummy_tool" in caplog.text

def test_register_invalid_callable(registry):
    """Test registering a non-callable raises ValueError."""
    with pytest.raises(ValueError, match="Tool invalid_tool must be a callable function."):
        registry.register("invalid_tool", "not_a_function")

def test_invoke_success(registry, caplog):
    """Test invoking a registered tool works and returns expected result."""
    def add_tool(a, b):
        return a + b

    registry.register("add", add_tool)

    with caplog.at_level(logging.INFO):
        result = registry.invoke("add", a=10, b=5)

    assert result == 15
    assert "Invoking tool: add" in caplog.text

def test_invoke_with_kwargs(registry):
    """Test invoking passes keyword arguments correctly."""
    def kwargs_tool(**kwargs):
        return kwargs

    registry.register("kwargs_tool", kwargs_tool)
    result = registry.invoke("kwargs_tool", key="value", number=42)

    assert result == {"key": "value", "number": 42}

def test_invoke_not_found(registry, caplog):
    """Test invoking a missing tool returns error dict and logs error."""
    with caplog.at_level(logging.ERROR):
        result = registry.invoke("non_existent_tool")

    assert isinstance(result, dict)
    assert result["status"] == "error"
    assert "Tool not found: non_existent_tool" in result["message"]
    assert "Tool not found: non_existent_tool" in caplog.text

def test_invoke_exception(registry, caplog):
    """Test tool execution failure is caught, returns error dict, and logs exception."""
    def failing_tool():
        raise RuntimeError("Something went wrong!")

    registry.register("failing_tool", failing_tool)

    with caplog.at_level(logging.ERROR):
        result = registry.invoke("failing_tool")

    assert isinstance(result, dict)
    assert result["status"] == "error"
    assert "Something went wrong!" in result["message"]
    assert "Tool execution failed: failing_tool" in caplog.text

def test_concurrency(registry):
    """Test thread safety during concurrent registrations."""
    def worker(i):
        registry.register(f"tool_{i}", lambda: i)

    threads = []
    for i in range(100):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    assert len(registry._tools) == 105
    for i in range(100):
        tool_name = f"tool_{i}"
        assert tool_name in registry._tools
        assert registry.invoke(tool_name) == i
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
from core.tools.registry import ToolRegistry

class TestToolRegistry:
    @pytest.fixture
    def registry(self):
        """Fixture to provide a fresh ToolRegistry instance for each test."""
        return ToolRegistry()

    def test_register_happy_path(self, registry):
        """Test registering a valid callable function."""
        def dummy_tool(x):
            return x * 2

        registry.register("dummy", dummy_tool)
        assert registry._tools["dummy"] == dummy_tool

    def test_register_not_callable(self, registry):
        """Test that registering a non-callable raises ValueError."""
        with pytest.raises(ValueError, match="must be a callable function"):
            registry.register("bad_tool", "not_a_function")

    def test_invoke_happy_path(self, registry):
        """Test invoking a registered tool successfully."""
        def add(a, b):
            return a + b

        registry.register("add", add)
        result = registry.invoke("add", a=5, b=3)
        assert result == 8

    def test_invoke_tool_not_found(self, registry):
        """Test invoking a tool that has not been registered."""
        result = registry.invoke("non_existent_tool")
        assert result["status"] == "error"
        assert "Tool not found" in result["message"]

    def test_invoke_exception(self, registry):
        """Test that exceptions raised by tools are caught and returned as errors."""
        def broken_tool():
            raise ValueError("Something went wrong")

        registry.register("broken", broken_tool)
        result = registry.invoke("broken")
        assert result["status"] == "error"
        assert "Something went wrong" in result["message"]
