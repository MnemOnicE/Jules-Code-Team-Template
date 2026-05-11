import re

file_path = "template_source/scripts/init_project.py"
with open(file_path, "r") as f:
    content = f.read()

# Revert adding 'src' to ignored_items
content = re.sub(
    r"ignored_items = \{'\.git', 'template_source', 'README\.md', 'LICENSE', 'CONTRIBUTING\.md', '\.DS_Store', 'src', 'tests', 'requirements\.txt', 'package\.json', 'package-lock\.json', '\.agents'\}",
    "ignored_items = {'.git', 'template_source', 'README.md', 'LICENSE', 'CONTRIBUTING.md', '.DS_Store', 'tests', 'requirements.txt', 'package.json', 'package-lock.json', '.agents'}",
    content
)

with open(file_path, "w") as f:
    f.write(content)

print("Reverted 'src' in ignored_items in init_project.py")
