import re

file_path = 'tests/test_init_project.py'
with open(file_path, 'r') as f:
    content = f.read()

# Since `configure_llm_providers` is imported locally inside the `main` function in `init_project.py`, patching it at the module level doesn't work.
# We have to patch `builtins.input` enough times to handle it.

# Genesis inputs: 11 inputs
# 'TestProject' -> Project Name
# 'SaaS' -> Project Context
# 'Democracy' -> Governance
# 'Low' -> Risk Tolerance
# 'Y' -> Ready to proceed
# 'n' -> OpenAI
# 'n' -> Gemini
# 'n' -> Jules API
# 'n' -> Ollama
# 'n' -> Llama.cpp

search_genesis = "mock_input.side_effect = ['TestProject', 'SaaS', 'Democracy', 'Low', 'Y', '', 'n', 'n', 'n', 'n', 'n']  # Added LLM config inputs"
replace_genesis = "mock_input.side_effect = ['TestProject', 'SaaS', 'Democracy', 'Low', 'Y', 'n', 'n', 'n', 'n', 'n']"

search_migration = "mock_input.side_effect = ['ExistingProject', 'Legacy Codebase', 'Dictator', 'High', 'Y', 'n', 'n', 'n', 'n', 'n']  # Added LLM config inputs"
replace_migration = "mock_input.side_effect = ['ExistingProject', 'Legacy Codebase', 'Dictator', 'High', 'Y', 'n', 'n', 'n', 'n', 'n']"


content = content.replace(search_genesis, replace_genesis)
content = content.replace(search_migration, replace_migration)

with open(file_path, 'w') as f:
    f.write(content)
