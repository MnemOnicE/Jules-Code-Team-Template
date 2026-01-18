#!/usr/bin/env python3
import argparse
import sys
import json
import uuid

# Imports
try:
    from src.core.bus import NexusBus
    from src.core.context import load_context
    from src.core.tools.graph_executor import GraphExecutor
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

def generate_mock_graph(task_description):
    """
    Generates a static execution graph for demonstration.
    Adheres to src/core/schema/execution_graph.json
    """
    graph_id = str(uuid.uuid4())

    return {
        "graph_id": graph_id,
        "intent_glyph": "🛡️🤖",
        "aether_mark": "mock_signature_verified",
        "entry_point": "node_1",
        "context_delta": {},
        "nodes": {
            "node_1": {
                "action": "logic_gate",
                "params": {
                    "condition": "Is task valid?"
                },
                "on_success": "node_2",
                "on_failure": "node_fail"
            },
            "node_2": {
                "action": "run_tool",
                "params": {
                    "tool": "plan_decomposition",
                    "args": {"task": task_description}
                },
                "on_success": "node_3"
            },
            "node_3": {
                "action": "write_file",
                "params": {
                    "filepath": "plan.txt",
                    "content": f"Plan for: {task_description}"
                },
                "next": "node_4"
            },
            "node_4": {
                "action": "terminate",
                "params": {}
            },
            "node_fail": {
                 "action": "terminate",
                 "params": {}
            }
        }
    }

def main():
    parser = argparse.ArgumentParser(description="Agent System V3 Command Interface")
    parser.add_argument("--task", type=str, help="The natural language task to perform")
    parser.add_argument("--file", type=str, help="A file to process")

    args = parser.parse_args()

    if not args.task and not args.file:
        parser.print_help()
        sys.exit(0)

    task = args.task or f"Process file: {args.file}"

    print("\n🔮 \033[1mInitializing Agent System V3...\033[0m")

    # 1. Initialize Bus (Nervous System)
    try:
        bus = NexusBus()
        print("✅ NexusBus Online")
    except Exception as e:
        print(f"❌ Failed to initialize NexusBus: {e}")
        # Continue mostly, or exit?
        # If bus fails (e.g. schema missing), we should probably fail.
        sys.exit(1)

    # 2. Load Context (Cortex Loader)
    try:
        brain_context = load_context("brain")
        print(f"✅ Loaded Persona: {brain_context['role']}")
    except Exception as e:
        print(f"❌ Failed to load context: {e}")
        sys.exit(1)

    # 3. Generate Execution Graph (Brain)
    print(f"🧠 Brain: Analyzing task: '{task}'")
    graph = generate_mock_graph(task)
    print(f"✅ Generated Execution Graph ({graph['graph_id']})")

    # 4. Execute (Muscles)
    print("\n🚀 \033[1mExecuting Graph...\033[0m")
    executor = GraphExecutor()
    executor.execute(graph)

    print("\n✨ Mission Complete.")

if __name__ == "__main__":
    main()
