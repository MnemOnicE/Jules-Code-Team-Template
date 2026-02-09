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

import json
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
    def __init__(self, event_bus: NexusBus):
        self.bus = event_bus
        self.registry = ToolRegistry()
        self.logger = logging.getLogger("Axion.Executor")

    def validate_integrity(self, graph: dict):
        """
        Zero-Trust Check: Does the intent_glyph match the graph actions?
        (In a real impl, this would verify the AetherMark).
        """
        glyph = graph.get("intent_glyph", "")
        self.logger.info(f"Validating graph against intent: {glyph}")
        # Enforcement of the "Shield" protocol (Source [2])
        if "🛡️" in glyph and "security_scan" not in str(graph):
            raise SecurityError("Graph deviates from Sentinel Intent! Halting.")

    def execute(self, graph: dict):
        self.validate_integrity(graph)
        context = graph.get("context_delta", {})
        current_node_id = graph["entry_point"]

        while current_node_id and current_node_id != "END":
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
                    current_node_id = node.get("on_failure")

                    # Recursive Logic (Source [2])
                    if context.get("retry_on_fail") and context.get("retry_count", 0) < 3:
                        self.logger.warning("Triggering Self-Correction Loop...")
                        context["retry_count"] = context.get("retry_count", 0) + 1
                        # In a real graph, this would loop back to a repair node defined in on_failure
                    elif context.get("retry_on_fail"):
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
