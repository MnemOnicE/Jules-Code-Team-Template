import re

file_path = "template_source/.agents/engine/core/tools/graph_executor.py"
with open(file_path, "r") as f:
    content = f.read()

# Add import at the top
if "from core.plugin_manager import plugin_manager" not in content:
    content = content.replace("from core.tools.registry import ToolRegistry",
                              "from core.tools.registry import ToolRegistry\nfrom core.plugin_manager import plugin_manager")

# Modify execute loop
execute_target = """            self.logger.info(f"[EXECUTING] Node {current_node_id}: {node['action']}")

            # Execute Action via Registry
            try:
                result = self._dispatch_action(node, graph_state)"""

execute_replacement = """            self.logger.info(f"[EXECUTING] Node {current_node_id}: {node['action']}")

            # Telemetry: Node Start
            plugin_manager.call_plugin_hook('on_node_start', {'id': current_node_id, 'data': node})

            # Telemetry: CoT Thought
            thought = node.get("reasoning") or node.get("thought") or node.get("description")
            if thought:
                plugin_manager.call_plugin_hook('on_cot_thought', thought)
            else:
                intent = node.get('action', 'unknown')
                plugin_manager.call_plugin_hook('on_cot_thought', f"Evaluating node {current_node_id}: {intent}")

            # Execute Action via Registry
            try:
                result = self._dispatch_action(node, graph_state)
                # Telemetry: Node Complete (Success)
                plugin_manager.call_plugin_hook('on_node_complete', {'id': current_node_id, 'status': 'success', 'error': None})"""

content = content.replace(execute_target, execute_replacement)

# Modify the except block in execute loop
except_target = """            except Exception as e:
                self.logger.critical(f"Graph Crash: {e}")
                break"""

except_replacement = """            except Exception as e:
                self.logger.critical(f"Graph Crash: {e}")
                plugin_manager.call_plugin_hook('on_node_complete', {'id': current_node_id, 'status': 'failed', 'error': str(e)})
                break"""

content = content.replace(except_target, except_replacement)

# Modify _dispatch_action
dispatch_target = """            if not tool_name:
                self.logger.error("Missing 'tool' in 'params' for 'run_tool' action.")
                return {"status": "error", "message": "Missing tool name for run_tool action"}

            return self.registry.invoke(tool_name, **args)"""

dispatch_replacement = """            if not tool_name:
                self.logger.error("Missing 'tool' in 'params' for 'run_tool' action.")
                return {"status": "error", "message": "Missing tool name for run_tool action"}

            result = self.registry.invoke(tool_name, **args)
            plugin_manager.call_plugin_hook('on_tool_invoke', {'tool': tool_name, 'args': args, 'result': result})
            return result"""

content = content.replace(dispatch_target, dispatch_replacement)

with open(file_path, "w") as f:
    f.write(content)
