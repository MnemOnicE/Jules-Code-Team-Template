import re

file_path = 'tests/test_init_project.py'
with open(file_path, 'r') as f:
    content = f.read()

# Fix mock inputs to include answers for LLM setup prompt
# The prompts in LLM setup:
# Use OpenAI? [y]
# OpenAI API Key:
# Use Gemini? [n]
# Use Jules API? [n]
# Use Ollama? [n]
# Use Llama.cpp? [n]

search_genesis = "mock_input.side_effect = ['TestProject', 'SaaS', 'Democracy', 'Low', '']  # Empty for git remote"
replace_genesis = "mock_input.side_effect = ['TestProject', 'SaaS', 'Democracy', 'Low', 'Y', '', 'n', 'n', 'n', 'n', 'n']  # Added LLM config inputs"

search_migration = "mock_input.side_effect = ['ExistingProject', 'Legacy Codebase', 'Dictator', 'High', '']  # Empty for git remote"
replace_migration = "mock_input.side_effect = ['ExistingProject', 'Legacy Codebase', 'Dictator', 'High', 'Y', 'n', 'n', 'n', 'n', 'n']  # Added LLM config inputs"

search_dry_run = "mock_input.side_effect = ['TestProject', 'SaaS', 'Democracy', 'Low', 'Y']"
replace_dry_run = "mock_input.side_effect = ['TestProject', 'SaaS', 'Democracy', 'Low', 'Y', 'n', 'n', 'n', 'n', 'n']"


content = content.replace(search_genesis, replace_genesis)
content = content.replace(search_migration, replace_migration)
content = content.replace(search_dry_run, replace_dry_run)

with open(file_path, 'w') as f:
    f.write(content)
print("Replaced successfully!")
