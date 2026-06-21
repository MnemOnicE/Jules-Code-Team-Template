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

import os
import logging


def _is_safe_path(path, root=None):
    """Checks if a path is safely contained within the specified root directory."""
    if root is None:
        root = os.getcwd()

    # Resolve all symbolic links and normalize the paths
    abs_path = os.path.realpath(os.path.abspath(path))
    abs_root = os.path.realpath(os.path.abspath(root))

    try:
        return os.path.commonpath([abs_root, abs_path]) == abs_root
    except ValueError:
        return False

def system_io_bridge(action):
    """Resilient bridge for filesystem operations with fuzzy argument mapping."""
    def bridge(**kwargs):
        logging.warning(f"Sentinel: Native implementation missing. Executing fallback bridge for '{action}'.")
        try:
            # Omnivore extraction: hunt for path and content regardless of key name
            path = kwargs.get('path') or kwargs.get('file_path') or kwargs.get('directory') or kwargs.get('filename')
            content = kwargs.get('content') or kwargs.get('text') or kwargs.get('data')
            if action == "mkdir":
                if not path: return {"status": "error", "message": "mkdir: No path provided."}
                if not _is_safe_path(path):
                    return {"status": "error", "message": f"Security Warning: Blocked out-of-bounds path: {path}"}
                os.makedirs(path, exist_ok=True)
                return {"status": "success", "path": os.path.abspath(path)}
            if action == "write":
                path = path or "test_flight.txt"
                if not _is_safe_path(path):
                    return {"status": "error", "message": f"Security Warning: Blocked out-of-bounds path: {path}"}
                dir_name = os.path.dirname(os.path.abspath(path))
                if dir_name: os.makedirs(dir_name, exist_ok=True)
                with open(path, 'w') as f:
                    f.write(str(content or ""))
                return {"status": "success", "file": path, "size": len(str(content or ""))}
            if action == "read":
                if not path:
                    return {"status": "error", "message": f"read: No path provided."}
                if not _is_safe_path(path):
                    return {"status": "error", "message": f"Security Warning: Blocked out-of-bounds path: {path}"}
                if not os.path.exists(path):
                    return {"status": "error", "message": f"read: File not found: {path}"}
                with open(path, 'r') as f:
                    return {"status": "success", "content": f.read(1_000_000)}



        except Exception as e:
            return {"status": "error", "message": str(e)}
    return bridge

class ToolRegistry:
    def __init__(self):
        self._tools = {}
        self.logger = logging.getLogger(__name__)

        # PROACTIVE REGISTRATION:
        # This ensures that even if the 'plugins' are missing, the Brain always has 'Hands'.
        CORE_MAP = {
            "write_file": "write",
            "directory": "mkdir",
            "mkdir": "mkdir",
            "read_file": "read",
            "create_file": "write"
        }
        for tool_name, action in CORE_MAP.items():
            # Silently pre-populate registry
            self._tools[tool_name] = system_io_bridge(action)

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
