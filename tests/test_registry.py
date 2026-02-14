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
from src.core.tools.registry import ToolRegistry

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
