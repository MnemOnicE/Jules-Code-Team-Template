import re

file_path = 'tests/test_init_project.py'
with open(file_path, 'r') as f:
    content = f.read()

# We need to mock `configure_llm_providers` so we don't hit the `input()` calls
search_genesis = "@patch('init_project.subprocess.run')"
replace_genesis = "@patch('init_project.subprocess.run')\n    @patch('init_project.configure_llm_providers')"

search_genesis_def = "def test_integration_genesis_mode(mock_subprocess, mock_install_hooks, mock_configure_git,"
replace_genesis_def = "def test_integration_genesis_mode(mock_configure_llm, mock_subprocess, mock_install_hooks, mock_configure_git,"

search_migration = "def test_integration_migration_mode(mock_print_header, mock_clear_screen, mock_input):"
replace_migration = "@patch('init_project.configure_llm_providers')\n    def test_integration_migration_mode(mock_configure_llm, mock_print_header, mock_clear_screen, mock_input):"


content = content.replace(search_genesis, replace_genesis)
content = content.replace(search_genesis_def, replace_genesis_def)
content = content.replace(search_migration, replace_migration)

with open(file_path, 'w') as f:
    f.write(content)
print("Replaced successfully!")
