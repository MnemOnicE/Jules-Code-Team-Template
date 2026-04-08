import re

file_path = 'tests/test_init_project.py'
with open(file_path, 'r') as f:
    content = f.read()

# Easiest way: just mock `core.llm_config.configure_llm_providers` inside the test functions right before main() is called using a context manager.
# Because the `configure_llm_providers` runs interactively and hits the `sys.exit(1)` or fails due to `input()`,
# we can just patch it out entirely during `main()`.

search = "from init_project import main\n            main()"
replace = "from init_project import main\n            with patch('core.llm_config.configure_llm_providers'):\n                main()"

content = content.replace(search, replace)

search_dry_run = "mock_input.side_effect = ['TestProject', 'SaaS', 'Democracy', 'Low']"
replace_dry_run = "mock_input.side_effect = ['TestProject', 'SaaS', 'Democracy', 'Low', 'Y']"
content = content.replace(search_dry_run, replace_dry_run)

with open(file_path, 'w') as f:
    f.write(content)
