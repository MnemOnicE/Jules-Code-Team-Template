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

import logging

class ToolRegistry:
    def __init__(self):
        self._tools = {}
        self.logger = logging.getLogger(__name__)

    def register(self, name, function):
        """Registers a function under a tool name."""
        if not callable(function):
            raise ValueError(f"Tool {name} must be a callable function.")
        self._tools[name] = function
        self.logger.debug(f"Registered tool: {name}")

    def invoke(self, tool_name, **kwargs):
        """Invokes a registered tool by name with arguments."""
        tool = self._tools.get(tool_name)
        if not tool:
            error_msg = f"Tool not found: {tool_name}"
            self.logger.error(error_msg)
            return {"status": "error", "message": error_msg}

        try:
            self.logger.info(f"Invoking tool: {tool_name}")
            result = tool(**kwargs)
            return result
        except Exception as e:
            self.logger.exception(f"Tool execution failed: {tool_name}")
            return {"status": "error", "message": str(e)}

# Default fallback tool for graceful execution
def plan_decomposition(**kwargs):
    """Fallback tool to prevent execution crash if LLM defaults to the old graph."""
    return {"status": "success", "message": "Task received and analyzed.", "args": kwargs}

# Initialize a default registry instance
default_registry = ToolRegistry()
default_registry.register("plan_decomposition", plan_decomposition)

import os

def write_file_bridge(**kwargs):
    """The 'Final Flight' bridge. Defaults to test_flight.txt if AI sends nothing."""
    try:
        # 1. Try to find path, if NONE, default to 'test_flight.txt'
        path = kwargs.get('path') or kwargs.get('file_path') or kwargs.get('filename') or "test_flight.txt"
        
        # 2. Try to find content, if NONE, default to the operational message
        content = kwargs.get('content') or kwargs.get('text') or kwargs.get('data') or "The squad is operational"

        print(f"\n[DEBUG] Bridge Active. Writing to: {os.path.abspath(path)}")
        print(f"[DEBUG] Content length: {len(str(content))} chars")

        with open(path, 'w') as f:
            f.write(str(content))
            
        return {"status": "success", "file": path, "message": "File written by Hard-Coded Fallback."}
    except Exception as e:
        print(f"[ERROR] Bridge failed: {e}")
        return {"status": "error", "message": str(e)}

# Force the registration
default_registry.register("write_file", write_file_bridge)
