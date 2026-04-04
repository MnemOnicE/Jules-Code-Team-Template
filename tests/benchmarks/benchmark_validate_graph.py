import timeit
import sys
import os
import contextlib

# Add src to path if run from root
sys.path.append(os.getcwd())

from core.bus import NexusBus

@contextlib.contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout

def benchmark_validate_graph():
    bus = NexusBus()

    valid_graph = {
        "graph_id": "test-uuid-1234",
        "intent_glyph": "🧪",
        "entry_point": "start_node",
        "nodes": {
            "start_node": {
                "action": "run_tool",
                "params": {"tool": "test_tool"},
                "on_success": "end_node"
            },
            "end_node": {
                "action": "terminate"
            }
        }
    }

    # Verify it works first
    try:
        # We want to see this output if it fails
        bus.validate_graph(valid_graph)
    except Exception as e:
        print(f"Initial validation failed: {e}")
        return

    # 10,000 iterations
    number = 10000

    with suppress_stdout():
        execution_time = timeit.timeit(lambda: bus.validate_graph(valid_graph), number=number)

    print(f"validate_graph ({number} calls): {execution_time:.6f} seconds")
    print(f"Average time per call: {execution_time/number:.9f} seconds")

if __name__ == "__main__":
    print("--- validate_graph Benchmark ---")
    benchmark_validate_graph()
