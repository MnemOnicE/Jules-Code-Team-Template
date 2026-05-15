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
# Note: Ensure core.bus is implemented as requested previously
from core.bus import NexusBus
from core.tools.registry import ToolRegistry
from core.plugin_manager import plugin_manager


class SecurityError(Exception):
    pass

class MaxStepsExceededError(Exception):
    pass

PRIVILEGED_TOOLS = {"execute_command", "write_file", "update_memory"}

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
        # Enforcement of the "Shield" protocol (Source [2])
        if "🛡️" in glyph and "security_scan" not in str(graph):
            raise SecurityError("Graph deviates from Sentinel Intent! Halting.")

        # Structural Traversal (DFS) to enforce security_scan for privileged tools
        entry_point = graph.get("entry_point")
        nodes = graph.get("nodes", {})

        if not entry_point or entry_point not in nodes:
            return

        visited = set()

        def dfs(node_id, has_been_scanned):
            # To handle cycles, if we've visited this node with the current scan state, return
            state_key = (node_id, has_been_scanned)
            if state_key in visited:
                return
            visited.add(state_key)

            if node_id == "END":
                return

            node = nodes.get(node_id)
            if not node:
                return

            # Update scan state
            current_scan_state = has_been_scanned
            if node.get("action") == "security_scan":
                current_scan_state = True

            # Check privileged tool violation
            if node.get("action") == "run_tool":
                tool_name = node.get("params", {}).get("tool")
                if tool_name in PRIVILEGED_TOOLS and not current_scan_state:
                    raise SecurityError(f"Security violation: Node '{node_id}' invokes privileged tool '{tool_name}' without prior security_scan.")

            # Traverse children
            next_nodes = []
            if "on_success" in node:
                next_nodes.append(node["on_success"])
            if "on_failure" in node:
                next_nodes.append(node["on_failure"])
            if "next" in node:
                next_nodes.append(node["next"])

            for next_node in next_nodes:
                if next_node:
                    dfs(next_node, current_scan_state)

        dfs(entry_point, False)

    def execute(self, graph: dict, system_context: dict = None):
        # 1. Structural Validation (The "Smart Worker" approach)
        self.bus.validate_graph(graph)

        # 2. Security Validation
        self.validate_integrity(graph)

        # State Segregation
        system_context = system_context or {}
        context = graph.get("context_delta", {})

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

            # Validate node-defined context_delta before applying it
            node_delta = node.get("context_delta", {})
            if any(k in system_context for k in node_delta):
                raise SecurityError(f"Node '{current_node_id}' attempted to overwrite protected system context keys.")

            # Apply allowed deltas to context
            context.update(node_delta)

            # Create merged view for action execution
            merged_view = {**context, **system_context}

            # Execute Action via Registry
            try:
                result = self._dispatch_action(node, merged_view)
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

    def _dispatch_action(self, node, merged_view):
    def _dispatch_action(self, node, graph_state):
        # Maps graph actions to specific tool calls
        action = node['action']
        if action == 'run_tool':
            params = node.get('params', {})
            tool_name = params.get('tool')
            args = params.get('args', {}).copy()
            # Inject context if needed (Source [1])
            if merged_view.get("shizuku_active"):
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
