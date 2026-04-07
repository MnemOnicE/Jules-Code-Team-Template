import re

file_path = "template_source/.agents/engine/core/tools/graph_executor.py"
with open(file_path, "r") as f:
    content = f.read()

# Fix default privileged_tools back to original. "read_file" is probably what caused the failure.
content = content.replace('self.privileged_tools = privileged_tools if privileged_tools is not None else {"execute_command", "write_file", "read_file"}',
                          'self.privileged_tools = privileged_tools if privileged_tools is not None else {"execute_command", "write_file", "update_memory"}')

with open(file_path, "w") as f:
    f.write(content)
