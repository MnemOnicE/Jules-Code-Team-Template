import re

with open("template_source/.agents/engine/core/bus.py", "r") as f:
    content = f.read()

pattern = r'        """\n        Legacy execution method for NexusBus\.\n        Delegates to GraphExecutor for traversal\.\n        Used by existing tests in tests/test_bus\.py\.\n\n        Args:\n            graph \(dict\): The execution graph to process\.\n            registry \(ToolRegistry, optional\): A custom tool registry to use for execution\.\n        """\n        """\n        Legacy execution method for NexusBus\.\n        Delegates to GraphExecutor for traversal\.\n        Used by existing tests in tests/test_bus\.py\.\n        """'
replacement = '''        """
        Legacy execution method for NexusBus.
        Delegates to GraphExecutor for traversal.
        Used by existing tests in tests/test_bus.py.

        Args:
            graph (dict): The execution graph to process.
            registry (ToolRegistry, optional): A custom tool registry to use for execution.
        """'''

content = re.sub(pattern, replacement, content)

with open("template_source/.agents/engine/core/bus.py", "w") as f:
    f.write(content)
