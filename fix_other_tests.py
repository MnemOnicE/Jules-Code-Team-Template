import re

with open("tests/test_context.py", "r") as f:
    content = f.read()

content = content.replace('    with patch("core.context.get_repo_root", return_value="/mock/repo/root"):\n    with patch("core.context.__file__", mock_file_path):', '    with patch("core.context.get_repo_root", return_value="/mock/repo/root"):\n        with patch("core.context.__file__", mock_file_path):')

with open("tests/test_context.py", "w") as f:
    f.write(content)

with open("tests/test_graph_executor.py", "r") as f:
    content = f.read()

content = content.replace('        with patch.object(executor.plugin_manager, "execute", side_effect=executor._built_in_tools):\n        with pytest.raises(SecurityError, match="Graph deviates from Sentinel Intent! Privileged tool \'write_file\' accessed before security_scan. Halting."):', '        with patch.object(executor.plugin_manager, "execute", side_effect=executor._built_in_tools):\n            with pytest.raises(SecurityError, match=re.escape("Graph deviates from Sentinel Intent! Privileged tool \'write_file\' accessed before security_scan. Halting.")):')
# Just simple replacement first
content = content.replace('        with pytest.raises(SecurityError, match="Graph deviates from Sentinel Intent! Privileged tool \'write_file\' accessed before security_scan. Halting."):', '            with pytest.raises(SecurityError, match=re.escape("Graph deviates from Sentinel Intent! Privileged tool \'write_file\' accessed before security_scan. Halting.")):')

with open("tests/test_graph_executor.py", "w") as f:
    f.write(content)
