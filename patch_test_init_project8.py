import re

file_path = 'tests/test_init_project.py'
with open(file_path, 'r') as f:
    content = f.read()

# I see the issue. `configure_llm_providers` has its own `input()` call internally, it doesn't use the same `input()` that was patched for `init_project` because it does `def get_input(...)` which calls `input()`.
# However, because `configure_llm_providers` is imported at the end of `main` inside `init_project.py` dynamically:
#    import sys
#    sys.path.insert(0, os.path.join(ROOT, ".agents", "engine"))
#    from core.llm_config import configure_llm_providers
#    configure_llm_providers()
#
# The simplest fix is to patch `core.llm_config.input` instead of `init_project.configure_llm_providers`

search_genesis = """    @patch('init_project.subprocess.run')

    def test_integration_genesis_mode(mock_subprocess, mock_install_hooks, mock_configure_git,"""
replace_genesis = """    @patch('init_project.subprocess.run')
    @patch('core.llm_config.input')
    def test_integration_genesis_mode(mock_llm_input, mock_subprocess, mock_install_hooks, mock_configure_git,"""

search_genesis2 = """mock_input.side_effect = ['TestProject', 'SaaS', 'Democracy', 'Low', 'Y'] + ['n'] * 20"""
replace_genesis2 = """mock_input.side_effect = ['TestProject', 'SaaS', 'Democracy', 'Low', 'Y']
        mock_llm_input.side_effect = ['n'] * 20"""


search_migration = """    @patch('init_project.print_header')

    def test_integration_migration_mode(mock_print_header, mock_clear_screen, mock_input):"""
replace_migration = """    @patch('init_project.print_header')
    @patch('core.llm_config.input')
    def test_integration_migration_mode(mock_llm_input, mock_print_header, mock_clear_screen, mock_input):"""

search_migration2 = """mock_input.side_effect = ['ExistingProject', 'Legacy Codebase', 'Dictator', 'High', 'Y'] + ['n'] * 20"""
replace_migration2 = """mock_input.side_effect = ['ExistingProject', 'Legacy Codebase', 'Dictator', 'High', 'Y']
        mock_llm_input.side_effect = ['n'] * 20"""


content = content.replace(search_genesis, replace_genesis)
content = content.replace(search_genesis2, replace_genesis2)
content = content.replace(search_migration, replace_migration)
content = content.replace(search_migration2, replace_migration2)


with open(file_path, 'w') as f:
    f.write(content)
