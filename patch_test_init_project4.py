import re

file_path = 'tests/test_init_project.py'
with open(file_path, 'r') as f:
    content = f.read()

# Fix mock input for dry run
search_dry_run = "mock_input.side_effect = ['TestProject', 'SaaS', 'Democracy', 'Low', 'Y', 'n', 'n', 'n', 'n', 'n']"
replace_dry_run = "mock_input.side_effect = ['TestProject', 'SaaS', 'Democracy', 'Low', 'Y', 'Y', 'n', 'n', 'n', 'n', 'n']"
content = content.replace(search_dry_run, replace_dry_run)
content = content.replace("mock_input.side_effect = ['TestProject', 'SaaS', 'Democracy', 'Low', 'Y']", replace_dry_run)
content = content.replace("mock_input.side_effect = ['TestProject', 'SaaS', 'Democracy', 'Low']", replace_dry_run)

# Fix patching configure_llm_providers, it is actually inside init_project main
content = content.replace("@patch('init_project.configure_llm_providers')", "")
content = content.replace("def test_integration_genesis_mode(mock_configure_llm, mock_subprocess, mock_install_hooks, mock_configure_git,", "def test_integration_genesis_mode(mock_subprocess, mock_install_hooks, mock_configure_git,")
content = content.replace("def test_integration_migration_mode(mock_configure_llm, mock_print_header, mock_clear_screen, mock_input):", "def test_integration_migration_mode(mock_print_header, mock_clear_screen, mock_input):")


with open(file_path, 'w') as f:
    f.write(content)
