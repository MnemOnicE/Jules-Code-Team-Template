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

    def test_system_io_bridge_write_unsafe_path(self, registry):
        """Test that writing to an unsafe path outside the root is blocked."""
        # Using a very long traversal to ensure we break out of current root
        unsafe_path = "../../../../../tmp/exploit.txt"

        # We need to invoke the write_file tool which uses system_io_bridge("write")
        result = registry.invoke("write_file", path=unsafe_path, content="exploit payload")

        assert result["status"] == "error"
        assert "Security Warning: Blocked out-of-bounds path" in result["message"]

    def test_system_io_bridge_read_unsafe_path(self, registry, tmp_path, monkeypatch):
        """Test that reading from an unsafe path outside the root is blocked."""
        # Create a file outside the "safe" root (by changing the working directory for the test)
        outside_file = tmp_path / "outside.txt"
        outside_file.write_text("secret")

        # Change current working directory to a subdirectory so tmp_path is outside
        safe_dir = tmp_path / "safe"
        safe_dir.mkdir()
        monkeypatch.chdir(safe_dir)

        # Try to read the file outside the safe directory
        result = registry.invoke("read_file", path=str(outside_file))

        assert result["status"] == "error"
        assert "Security Warning: Blocked out-of-bounds path" in result["message"]

    def test_system_io_bridge_mkdir_unsafe_path(self, registry):
        """Test that making a directory outside the root is blocked."""
        unsafe_path = "../../../../../tmp/exploit_dir"

        result = registry.invoke("mkdir", path=unsafe_path)

        assert result["status"] == "error"
        assert "Security Warning: Blocked out-of-bounds path" in result["message"]

    def test_system_io_bridge_safe_path(self, registry, tmp_path, monkeypatch):
        """Test that operations on safe paths within the root succeed."""
        monkeypatch.chdir(tmp_path)

        # Test mkdir
        safe_dir = "my_safe_dir"
        result_mkdir = registry.invoke("mkdir", path=safe_dir)
        assert result_mkdir["status"] == "success"

        # Test write
        safe_file = f"{safe_dir}/safe.txt"
        result_write = registry.invoke("write_file", path=safe_file, content="safe content")
        assert result_write["status"] == "success"

        # Test read
        result_read = registry.invoke("read_file", path=safe_file)
        assert result_read["status"] == "success"
        assert result_read["content"] == "safe content"
