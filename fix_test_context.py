with open("tests/test_context.py", "r") as f:
    lines = f.readlines()

with open("tests/test_context.py", "w") as f:
    for line in lines:
        if line.strip() == 'with patch("core.context.__file__", mock_file_path), \\':
            pass
        elif line.strip() == 'patch("pathlib.Path.exists", return_value=False), \\':
            pass
        elif line.strip() == 'patch.object(ContextLoader, \'_find_agents_dir\', return_value="/mock/agents"):':
            pass
        else:
            f.write(line)
