
import signal
from unittest.mock import MagicMock
from core.tools.graph_executor import GraphExecutor

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException

def test_infinite_loop():
    mock_bus = MagicMock()
    executor = GraphExecutor(event_bus=mock_bus)

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

    executor._dispatch_action = MagicMock(return_value={"status": "success"})

    # Set a timeout for the test
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(2)  # 2 seconds should be plenty if it's NOT infinite

    try:
        print("Starting infinite loop execution...")
        executor.execute(graph)
    except TimeoutException:
        print("Caught expected infinite loop (timeout)")
    except Exception as e:
        print(f"Caught unexpected exception: {e}")
    finally:
        signal.alarm(0)

if __name__ == "__main__":
    test_infinite_loop()
