import re

file_path = 'tests/test_infinite_loop_reproduction.py'
with open(file_path, 'r') as f:
    content = f.read()

content = content.replace("executor = GraphExecutor(event_bus=mock_bus)", "executor = GraphExecutor()")

with open(file_path, 'w') as f:
    f.write(content)
