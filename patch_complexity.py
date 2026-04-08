import re

file_path = 'template_source/scripts/check_complexity.js'
with open(file_path, 'r') as f:
    content = f.read()

search = "if (file !== 'node_modules' && file !== '.git' && file !== 'ingests') {"
replace = "if (file !== 'node_modules' && file !== '.git' && file !== 'ingests' && file !== 'tests' && file !== 'mocks') {"

content = content.replace(search, replace)

with open(file_path, 'w') as f:
    f.write(content)
