
import timeit
import sys
import os
import signal
from unittest.mock import MagicMock

# Add src to path if run from root
sys.path.append(os.getcwd())

# Mock jsonschema for NexusBus
from unittest.mock import MagicMock
import importlib.util
if importlib.util.find_spec("jsonschema") is None:
    jsonschema_mock = MagicMock()
    class ValidationError(Exception):
        def __init__(self, message, *args, **kwargs):
            self.message = message
            super().__init__(message, *args, **kwargs)
    jsonschema_mock.ValidationError = ValidationError
    sys.modules["jsonschema"] = jsonschema_mock
    sys.modules["jsonschema.validators"] = MagicMock()

from src.core.tools.graph_executor import GraphExecutor
from src.core.bus import NexusBus

class TimeoutException(BaseException):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException

def benchmark_linear_graph():
    bus = NexusBus()
    executor = GraphExecutor(event_bus=bus)
    executor.validate_integrity = MagicMock()
    executor._dispatch_action = MagicMock(return_value={"status": "success"})

    # Linear graph with 10 nodes
    nodes = {}
    for i in range(1, 11):
        next_node = f"node{i+1}" if i < 10 else "END"
        nodes[f"node{i}"] = {
            "action": "test_action",
            "next": next_node
        }

    graph = {
        "intent_glyph": "🧪",
        "entry_point": "node1",
        "nodes": nodes
    }

    number = 1000
    execution_time = timeit.timeit(lambda: executor.execute(graph), number=number)

    print(f"Linear graph (10 nodes, {number} calls): {execution_time:.6f} seconds")
    print(f"Average time per call: {execution_time/number:.9f} seconds")
    return execution_time / number

def benchmark_cyclic_graph():
    bus = NexusBus()
    executor = GraphExecutor(event_bus=bus)
    executor.validate_integrity = MagicMock()
    executor._dispatch_action = MagicMock(return_value={"status": "success"})

    # Cyclic graph: node1 -> node2 -> node1
    graph = {
        "intent_glyph": "🧪",
        "entry_point": "node1",
        "nodes": {
            "node1": {
                "action": "test_action",
                "next": "node2"
            },
            "node2": {
                "action": "test_action",
                "next": "node1"
            }
        }
    }

    # No timeout needed if it works correctly, but good for safety
    has_alarm = hasattr(signal, "SIGALRM")
    if has_alarm:
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(2)

    print("Benchmarking cyclic graph (should terminate via step limit)...")
    start_time = timeit.default_timer()
    try:
        executor.execute(graph)
        end_time = timeit.default_timer()
        print(f"Cyclic graph terminated via step limit in {end_time - start_time:.6f} seconds")
    except TimeoutException:
        print(f"Cyclic graph STILL timed out! Optimization failed.")
    finally:
        if has_alarm:
            signal.alarm(0)

if __name__ == "__main__":
    print("--- GraphExecutor Performance Results ---")
    avg_linear = benchmark_linear_graph()
    benchmark_cyclic_graph()
