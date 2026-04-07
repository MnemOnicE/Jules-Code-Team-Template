import re

file_path = "tests/test_graph_executor.py"
with open(file_path, "r") as f:
    content = f.read()

# We noticed tests are asserting specific privileged tools that we changed,
# but we shouldn't fail tests that were depending on a different privileged_tools set.
# Let's see what privileged_tools are default in tests.
print("Nothing to change yet, let's look at the tests.")
