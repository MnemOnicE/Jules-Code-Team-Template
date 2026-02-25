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
from src.core.bus import NexusBus
from src.core.tools.registry import ToolRegistry

class SecurityError(Exception):
    pass

class GraphExecutor:
    """
    Traverses the Sovereign Execution Graph.
    Acts as the 'Soldier' validating the 'General's' orders.
    """
    MAX_STEPS = 1000

    def __init__(self, event_bus: NexusBus):
        self.bus = event_bus
        self.registry = ToolRegistry()
        self.logger = logging.getLogger(__name__)

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

    def execute(self, graph: dict):
        self.validate_integrity(graph)
        context = graph.get("context_delta", {})
        current_node_id = graph["entry_point"]
        step_count = 0

        while current_node_id and current_node_id != "END":
            step_count += 1
            if step_count > self.MAX_STEPS:
                msg = f"Max steps ({self.MAX_STEPS}) exceeded. Potential infinite loop."
                self.logger.error(msg)
                raise MaxStepsExceededError(msg)

            node = graph["nodes"].get(current_node_id)
            if not node:
                self.logger.error(f"Node {current_node_id} not found.")
                break

            self.logger.info(f"Executing Node: {current_node_id} [{node['action']}]")

            # Execute Action via Registry
            try:
                result = self._dispatch_action(node, context)

                # Determine transition
                if result.get('status') == 'success':
                    current_node_id = node.get("on_success") or node.get("next")
                else:
                    # Capture the failure/repair node from the graph
                    repair_node = node.get("on_failure")

                    # Recursive Logic (Source [2])
                    if context.get("retry_on_fail") and context.get("retry_count", 0) < 3:
                        self.logger.warning("Triggering Self-Correction Loop...")
                        context["retry_count"] = context.get("retry_count", 0) + 1

                        # Implement Repair Loop:
                        # If a specific on_failure node exists, it's our repair node.
                        # If not, we "repair" by just retrying the current node.
                        current_node_id = repair_node if repair_node else current_node_id
                    else:
                        current_node_id = repair_node
                        if context.get("retry_on_fail"):
                             self.logger.error("Max retries exceeded. Aborting.")
                             break

            except Exception as e:
                self.logger.critical(f"Graph Crash: {e}")
                break

    def _dispatch_action(self, node, context):
        # Maps graph actions to specific tool calls
        if node['action'] == 'run_tool':
            tool_name = node['params']['tool']
            args = node['params'].get('args', {})
            # Inject context if needed (Source [1])
            if context.get("shizuku_active"):
                args["use_root"] = True

            return self.registry.invoke(tool_name, **args)

        return {"status": "success"} # Mock return for non-tool actions
