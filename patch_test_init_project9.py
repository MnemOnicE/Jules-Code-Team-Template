import re

file_path = 'tests/test_init_project.py'
with open(file_path, 'r') as f:
    content = f.read()

# Fix indent
content = content.replace("        mock_llm_input.side_effect = ['n'] * 20", "        mock_llm_input.side_effect = ['n'] * 20")

with open(file_path, 'w') as f:
    f.write(content)
