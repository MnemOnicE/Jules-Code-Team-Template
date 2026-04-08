import re

file_path = 'tests/test_init_project.py'
with open(file_path, 'r') as f:
    content = f.read()

# I am going to mock `init_project.configure_llm_providers` properly this time.

search_genesis = """    def test_integration_genesis_mode(mock_subprocess, mock_install_hooks, mock_configure_git,"""
replace_genesis = """    @patch('init_project.configure_llm_providers')
    def test_integration_genesis_mode(mock_configure_llm, mock_subprocess, mock_install_hooks, mock_configure_git,"""

search_migration = """    def test_integration_migration_mode(mock_print_header, mock_clear_screen, mock_input):"""
replace_migration = """    @patch('init_project.configure_llm_providers')
    def test_integration_migration_mode(mock_configure_llm, mock_print_header, mock_clear_screen, mock_input):"""


content = content.replace(search_genesis, replace_genesis)
content = content.replace(search_migration, replace_migration)


with open(file_path, 'w') as f:
    f.write(content)
