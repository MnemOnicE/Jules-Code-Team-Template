import re

file_path = "template_source/.agents/engine/core/tools/graph_executor.py"
with open(file_path, "r") as f:
    content = f.read()

# "delete_file" seems to be part of privileged_tools in tests. Let's add it back.
content = content.replace('self.privileged_tools = privileged_tools if privileged_tools is not None else {"execute_command", "write_file", "update_memory"}',
                          'self.privileged_tools = privileged_tools if privileged_tools is not None else {"execute_command", "write_file", "update_memory", "delete_file"}')

with open(file_path, "w") as f:
    f.write(content)
