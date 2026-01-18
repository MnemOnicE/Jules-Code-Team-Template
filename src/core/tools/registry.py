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
