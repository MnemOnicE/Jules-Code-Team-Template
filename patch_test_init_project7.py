import re

file_path = 'tests/test_init_project.py'
with open(file_path, 'r') as f:
    content = f.read()

# Try one more time, just mock `builtins.input` everywhere we need to, and provide it with a long enough list of side_effects

replace_genesis = "mock_input.side_effect = ['TestProject', 'SaaS', 'Democracy', 'Low', 'Y'] + ['n'] * 20"
replace_migration = "mock_input.side_effect = ['ExistingProject', 'Legacy Codebase', 'Dictator', 'High', 'Y'] + ['n'] * 20"

content = content.replace("mock_input.side_effect = ['TestProject', 'SaaS', 'Democracy', 'Low', 'Y', 'n', 'n', 'n', 'n', 'n']", replace_genesis)
content = content.replace("mock_input.side_effect = ['ExistingProject', 'Legacy Codebase', 'Dictator', 'High', 'Y', 'n', 'n', 'n', 'n', 'n']", replace_migration)


with open(file_path, 'w') as f:
    f.write(content)
