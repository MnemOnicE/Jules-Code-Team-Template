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
from core.tools.registry import ToolRegistry
from core.plugin_manager import plugin_manager




class SecurityError(Exception):

    pass

class MaxStepsExceededError(Exception):
    pass

class GraphExecutor:
    """
    Traverses the Sovereign Execution Graph.
    Acts as the 'Soldier' validating the 'General's' orders.
    """
    MAX_STEPS = 1000


    def __init__(self, bus, system_context=None, registry=None, privileged_tools=None):
        self.bus = bus
        self.context = system_context
        from core.tools.registry import default_registry
        self.registry = registry if registry is not None else default_registry
        import logging
        self.logger = logging.getLogger(__name__)
        self.system_context = system_context or {}
        self.privileged_tools = privileged_tools if privileged_tools is not None else {"execute_command", "write_file", "update_memory", "delete_file"}


    def validate_integrity(self, graph: dict):
        """
        Zero-Trust Check: Does the intent_glyph match the graph actions?
        (In a real impl, this would verify the AetherMark).
        """
        glyph = str(graph.get("intent_glyph") or "")
        self.logger.info(f"Validating graph against intent: {glyph}")

        # Enforcement of the "Shield" protocol
        if "🛡️" in glyph:
            entry_point = graph.get("entry_point")
            if not entry_point:
                return  # Empty graph, nothing to run

            nodes = graph.get("nodes", {})

            # DFS/BFS to find path to privileged tools
            from collections import deque
            queue = deque([(entry_point, False)]) # (node_id, has_passed_security_scan)
            visited = set()

            while queue:
                current_id, has_scanned = queue.popleft()

                # Check for cycle / visited with current scan status
                state = (current_id, has_scanned)
                if state in visited:
                    continue
                visited.add(state)

                if current_id == "END" or current_id not in nodes:
                    continue

                node = nodes[current_id]
                action = node.get("action")
                tool = node.get("params", {}).get("tool") if action == "run_tool" else None

                if action == "security_scan":
                    has_scanned = True
                elif action == "run_tool" and tool in self.privileged_tools and not has_scanned:
                    raise SecurityError(f"Graph deviates from Sentinel Intent! Privileged tool '{tool}' accessed before security_scan. Halting.")

                # Queue next nodes
                for next_key in ["next", "on_success", "on_failure"]:
                    next_id = node.get(next_key)
                    if next_id:
                        queue.append((next_id, has_scanned))
        else:
            # For non-shield intents, we still might want to ensure they aren't using string hacking,
            # but for now we just rely on the existing check
            pass

    def execute(self, graph: dict):
        # 1. Structural Validation (The "Smart Worker" approach)
        self.bus.validate_graph(graph)

        # 2. Security Validation
        self.validate_integrity(graph)
        graph_state = (graph.get("context_delta") or {}).copy()
        graph_state = graph.get("context_delta", {})

        # 3. Privilege Escalation Prevention (The "Captain's Orders" protocol)
        if self.system_context:
            protected_keys = set(self.system_context.keys())
            attempted_keys = set(graph_state.keys())
            violations = protected_keys.intersection(attempted_keys)
            if violations:
                msg = f"Security Violation: Graph attempted to overwrite protected system context keys: {violations}"
                self.logger.critical(msg)
                raise SecurityError(msg)
        current_node_id = graph["entry_point"]
        step_count = 0

        self.logger.info(f"[NEXUS] Starting execution at entry point: {current_node_id}")

        while current_node_id and current_node_id != "END":
            step_count += 1
            if step_count > self.MAX_STEPS:
                msg = f"Max steps ({self.MAX_STEPS}) exceeded. Potential infinite loop."
                self.logger.error(msg)
                raise MaxStepsExceededError(msg)

            node = graph["nodes"].get(current_node_id)
            if not node:
                self.logger.error(f"[ERROR] Node '{current_node_id}' not found in graph.")
                break

            self.logger.info(f"[EXECUTING] Node {current_node_id}: {node['action']}")

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
                plugin_manager.call_plugin_hook('on_node_complete', {'id': current_node_id, 'status': 'success', 'error': None})

                # Determine transition
                prev_id = current_node_id
                if result.get('status') == 'success':
                    current_node_id = node.get("on_success") or node.get("next")
                else:
                    # Capture the failure/repair node from the graph
                    repair_node = node.get("on_failure")

                    # Recursive Logic (Source [2])
                    if graph_state.get("retry_on_fail") and graph_state.get("retry_count", 0) < 3:
                        self.logger.warning("Triggering Self-Correction Loop...")
                        graph_state["retry_count"] = graph_state.get("retry_count", 0) + 1

                        # Implement Repair Loop:
                        # If a specific on_failure node exists, it's our repair node.
                        # If not, we "repair" by just retrying the current node.
                        current_node_id = repair_node if repair_node else current_node_id
                    else:
                        current_node_id = repair_node
                        if graph_state.get("retry_on_fail"):
                             self.logger.error("Max retries exceeded. Aborting.")
                             break

                if not current_node_id and node.get('action') != 'terminate':
                    self.logger.info(f"[NEXUS] No next node defined for {prev_id}. Stopping.")

            except Exception as e:
                self.logger.critical(f"Graph Crash: {e}")
                plugin_manager.call_plugin_hook('on_node_complete', {'id': current_node_id, 'status': 'failed', 'error': str(e)})
                break

    def _dispatch_action(self, node, graph_state):
        # Maps graph actions to specific tool calls
        action = node['action']
        if action == 'run_tool':
            params = node.get('params', {})
            tool_name = params.get('tool')
            args = params.get('args', {}).copy()
            # Inject context if needed (Source [1])
            if self.system_context.get("shizuku_active"):
                args["use_root"] = True

            if not tool_name:
                self.logger.error("Missing 'tool' in 'params' for 'run_tool' action.")
                return {"status": "error", "message": "Missing tool name for run_tool action"}

            result = self.registry.invoke(tool_name, **args)
            plugin_manager.call_plugin_hook('on_tool_invoke', {'tool': tool_name, 'args': args, 'result': result})
            return result

        if action == 'terminate':
            self.logger.info("[NEXUS] Terminate action reached. Stopping.")
            return {"status": "success"}

        return {"status": "success"} # Mock return for non-tool actions
