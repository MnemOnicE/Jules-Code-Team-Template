🎯 **What:**
Fixed a path traversal vulnerability in `template_source/scripts/init_project.py` and `template_source/scripts/backup_restore.py`. The previous implementation of directory boundary checking used `os.path.abspath` and string matching `.startswith()`, which failed to resolve symbolic links properly during unpacking operations.

⚠️ **Risk:**
If an attacker provided a crafted TAR archive or template folder containing symbolic links pointing to sensitive external directories (e.g., `../../../../etc/passwd`), the extraction process would write files outside the intended project root, potentially leading to arbitrary file overwrite or system compromise.

🛡️ **Solution:**
Updated `is_safe_path` in `init_project.py` and `_is_within_directory` in `backup_restore.py` to robustly combine `os.path.realpath(os.path.abspath(...))` to fully resolve symlinks, and `os.path.commonpath(...)` to strictly verify path prefixes. Additionally, removed pre-existing syntax errors (duplicate `with` blocks) in `tests/test_context.py` and `tests/test_graph_executor.py` that were blocking test suite collection, and added new unit tests ensuring that symlink escape vectors are securely blocked.
