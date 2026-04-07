import re

with open("tests/test_context.py", "r") as f:
    content = f.read()

pattern = r'# Calculate what we expect based on the mocked file path\n\s+# /usr/local/src/project/src/core/context\.py -> dirname -> \.\.\./src/core -> \.\. -> \.\.\./src -> \.\. -> \.\.\./project'
replacement = r'# Calculate what we expect based on the mocked file path\n                # /usr/local/src/project/src/core/context.py -> dirname -> .../src/core -> .. -> .../src -> .. -> .../project -> .. -> /usr/local/src'

content = re.sub(pattern, replacement, content)

with open("tests/test_context.py", "w") as f:
    f.write(content)
