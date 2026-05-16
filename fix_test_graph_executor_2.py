with open("tests/test_graph_executor.py", "r") as f:
    content = f.read()

content = content.replace('        with pytest.raises(SecurityError, match=re.escape("Graph deviates from Sentinel Intent! Privileged tool \'delete_file\' accessed before security_scan. Halting.")):\\n        with pytest.raises(SecurityError, match="Graph deviates from Sentinel Intent! Privileged tool \'delete_file\' accessed before security_scan. Halting."):', '        with pytest.raises(SecurityError, match=re.escape("Graph deviates from Sentinel Intent! Privileged tool \'delete_file\' accessed before security_scan. Halting.")):')
content = content.replace('    with pytest.raises(SecurityError, match=re.escape("Graph deviates from Sentinel Intent! Privileged tool \'delete_file\' accessed before security_scan. Halting.")):\\n    with pytest.raises(SecurityError, match="Graph deviates from Sentinel Intent! Privileged tool \'delete_file\' accessed before security_scan. Halting."):', '    with pytest.raises(SecurityError, match=re.escape("Graph deviates from Sentinel Intent! Privileged tool \'delete_file\' accessed before security_scan. Halting.")):')

# In case it's literal
lines = content.split('\n')
new_lines = []
for line in lines:
    if 'with pytest.raises(SecurityError, match="Graph deviates from Sentinel Intent! Privileged tool \'delete_file\' accessed before security_scan. Halting."):' in line:
        continue
    new_lines.append(line)

with open("tests/test_graph_executor.py", "w") as f:
    f.write('\n'.join(new_lines))
