import time
import json

class GraphExecutor:
    def __init__(self):
        pass

    def execute(self, graph_data):
        """
        Traverses the graph and simulates execution.
        Adheres to src/core/schema/execution_graph.json.
        """
        graph_id = graph_data.get('graph_id', 'unknown')
        entry_point = graph_data.get('entry_point')
        nodes = graph_data.get('nodes', {})

        print(f"[EXECUTOR] Starting Graph execution: {graph_id}")

        current_node_id = entry_point
        visited = set()

        # Safety limit for iterations to prevent infinite loops even if visited set logic fails for some DAG structures
        iterations = 0
        max_iterations = 100

        while current_node_id:
            iterations += 1
            if iterations > max_iterations:
                print("[EXECUTOR] Max iterations reached. Aborting.")
                break

            # In a DAG, we can visit a node multiple times if paths converge, but we shouldn't have cycles.
            # However, for simplicity here, we track path to avoid cycles?
            # The prompt says DAG.

            node = nodes.get(current_node_id)
            if not node:
                print(f"[EXECUTOR] Error: Node '{current_node_id}' not found.")
                break

            action = node.get('action')
            params = node.get('params', {})

            print(f"[EXECUTOR] >> Node {current_node_id} [{action}]")

            if action == 'terminate':
                print(f"    [TERM] Terminating sequence.")
                break

            # Execute Action
            success = self._perform_action(action, params)

            # Determine Transition
            # Priority: 'next' (Unconditional) > 'on_success'/'on_failure'

            next_node = node.get('next')

            if not next_node:
                if success:
                    next_node = node.get('on_success')
                else:
                    next_node = node.get('on_failure')

            if next_node:
                current_node_id = next_node
            else:
                # Terminal state
                print(f"[EXECUTOR] Node {current_node_id} finished with no transition. Execution End.")
                break

    def _perform_action(self, action, params):
        """
        Simulates the action execution.
        In a real system, this would call ToolRegistry.
        """
        # Mock implementations
        if action == 'run_tool':
            tool_name = params.get('tool')
            args = params.get('args')
            print(f"    [TOOL] Running {tool_name} with {args}")
            # Simulate tool output
            return True

        elif action == 'write_file':
            filepath = params.get('filepath')
            print(f"    [FILE] Writing to {filepath}")
            return True

        elif action == 'human_input':
            print(f"    [INPUT] Waiting for user input... (Simulated: 'Proceed')")
            return True

        elif action == 'logic_gate':
            condition = params.get('condition')
            print(f"    [LOGIC] Evaluating {condition} -> True")
            return True

        else:
            print(f"    [UNKNOWN] Action {action} not recognized.")
            return False
import json
import logging
# Note: Ensure core.bus is implemented as requested previously
from core.bus import NexusBus
from core.tools.registry import ToolRegistry

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
