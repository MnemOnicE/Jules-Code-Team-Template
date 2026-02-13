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
import logging
from src.core.tools.registry import ToolRegistry

@pytest.fixture
def registry():
    return ToolRegistry()

def test_register_happy_path_function(registry, caplog):
    """Test registering a standard function."""
    def sample_func(x):
        return x * 2

    with caplog.at_level(logging.DEBUG):
        registry.register("double", sample_func)

    assert "double" in registry._tools
    assert registry._tools["double"] == sample_func
    assert "Registered tool: double" in caplog.text

def test_register_happy_path_lambda(registry):
    """Test registering a lambda function."""
    registry.register("square", lambda x: x ** 2)
    assert "square" in registry._tools
    assert registry._tools["square"](3) == 9

def test_register_happy_path_method(registry):
    """Test registering a bound method."""
    class Multiplier:
        def __init__(self, factor):
            self.factor = factor

        def multiply(self, x):
            return x * self.factor

    m = Multiplier(5)
    registry.register("multiply_by_5", m.multiply)

    assert "multiply_by_5" in registry._tools
    assert registry._tools["multiply_by_5"](2) == 10

def test_register_error_non_callable(registry):
    """Test that registering a non-callable raises ValueError."""
    with pytest.raises(ValueError, match="Tool not_callable must be a callable function."):
        registry.register("not_callable", "I am a string")

def test_register_error_none(registry):
    """Test that registering None raises ValueError."""
    with pytest.raises(ValueError, match="Tool none_tool must be a callable function."):
        registry.register("none_tool", None)

def test_invoke_happy_path(registry):
    """Test invoking a registered tool."""
    def greet(name):
        return f"Hello, {name}!"

    registry.register("greet", greet)
    result = registry.invoke("greet", name="World")
    assert result == "Hello, World!"

def test_invoke_error_not_found(registry, caplog):
    """Test invoking a non-existent tool."""
    with caplog.at_level(logging.ERROR):
        result = registry.invoke("non_existent")

    assert result["status"] == "error"
    assert "Tool not found: non_existent" in result["message"]
    assert "Tool not found: non_existent" in caplog.text

def test_invoke_exception_handling(registry, caplog):
    """Test that exceptions during tool execution are caught and logged."""
    def buggy_tool():
        raise ValueError("Something went wrong")

    registry.register("buggy", buggy_tool)

    with caplog.at_level(logging.ERROR):
        result = registry.invoke("buggy")

    assert result["status"] == "error"
    assert "Something went wrong" in result["message"]
    assert "Tool execution failed: buggy" in caplog.text
