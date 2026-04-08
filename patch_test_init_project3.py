import re

file_path = 'tests/test_init_project.py'
with open(file_path, 'r') as f:
    content = f.read()

# Fix the indentation error
content = content.replace("    @patch('init_project.configure_llm_providers')\n    def test_integration_migration_mode", "    @patch('init_project.configure_llm_providers')\n    def test_integration_migration_mode")

with open(file_path, 'w') as f:
    f.write(content)
