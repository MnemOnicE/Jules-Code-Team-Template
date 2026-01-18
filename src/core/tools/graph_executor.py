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
