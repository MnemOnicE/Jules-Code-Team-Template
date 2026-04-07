import re

file_path = "tests/test_graph_executor.py"
with open(file_path, "r") as f:
    content = f.read()

# Replace event_bus with bus in fixture
content = content.replace("return GraphExecutor(event_bus=mock_bus)", "return GraphExecutor(bus=mock_bus)")

with open(file_path, "w") as f:
    f.write(content)
