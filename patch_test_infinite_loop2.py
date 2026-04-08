import re

file_path = 'tests/test_infinite_loop_reproduction.py'
with open(file_path, 'r') as f:
    content = f.read()

content = content.replace("executor = GraphExecutor()", "executor = GraphExecutor(bus=mock_bus)")

with open(file_path, 'w') as f:
    f.write(content)
