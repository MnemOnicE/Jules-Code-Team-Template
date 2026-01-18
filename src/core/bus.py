import json
import os
import jsonschema

class NexusBus:
    def __init__(self):
        # Locate the schema file relative to this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        schema_path = os.path.join(current_dir, 'schema', 'execution_graph.json')

        if not os.path.exists(schema_path):
             raise FileNotFoundError(f"Schema file not found at: {schema_path}")

        with open(schema_path, 'r') as f:
            self.schema = json.load(f)

    def validate_graph(self, graph_data):
        """Validates the given graph data against the Sovereign Execution Graph schema."""
        try:
            jsonschema.validate(instance=graph_data, schema=self.schema)
            print("[VALIDATION] Graph structure is valid.")
            return True
        except jsonschema.ValidationError as e:
            print(f"[VALIDATION ERROR] {e.message}")
            raise e

    def execute(self, graph_data):
        """Traverses the graph and simulates execution."""
        # 1. Validate
        self.validate_graph(graph_data)

        # 2. Start Traversal
        current_node_id = graph_data.get('entry_point')
        nodes = graph_data.get('nodes', {})

        print(f"[NEXUS] Starting execution at entry point: {current_node_id}")

        while current_node_id:
            node = nodes.get(current_node_id)
            if not node:
                print(f"[ERROR] Node '{current_node_id}' not found in graph.")
                break

            action = node.get('action')
            print(f"[EXECUTING] Node {current_node_id}: {action}")

            # Simulate logic / Determine next node
            if action == 'terminate':
                print("[NEXUS] Terminate action reached. Stopping.")
                break

            # Simple traversal logic (Happy Path)
            next_node = node.get('next')
            if not next_node:
                # If no unconditional jump, check for on_success
                next_node = node.get('on_success')

            if next_node:
                current_node_id = next_node
            else:
                print(f"[NEXUS] No next node defined for {current_node_id}. Stopping.")
                break
