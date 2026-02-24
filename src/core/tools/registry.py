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
        self.logger = logging.getLogger("Axion.Registry")

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
