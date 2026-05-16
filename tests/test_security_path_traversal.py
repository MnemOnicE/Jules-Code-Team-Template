import os
import sys
import pytest

# Ensure the scripts directory is in the path for importing
scripts_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "template_source", "scripts"))
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

from init_project import is_safe_path

def test_is_safe_path():
    root = "/test/root"
    assert is_safe_path("/test/root/safe/path", root) == True
    assert is_safe_path("/test/root/../out_of_bounds", root) == False
    assert is_safe_path("/test/root", root) == True
import tempfile

def test_is_safe_path_with_symlink():
    with tempfile.TemporaryDirectory() as root_dir:
        # Create a safe target inside root
        safe_target = os.path.join(root_dir, "safe_target")
        os.makedirs(safe_target)

        # Create an unsafe target outside root
        unsafe_target = tempfile.mkdtemp()

        try:
            # Create a symlink pointing outside the root
            symlink_path = os.path.join(root_dir, "malicious_link")
            os.symlink(unsafe_target, symlink_path)

            # This should be safe because it's physically located in root... wait, it points OUTSIDE root.
            # is_safe_path uses os.path.realpath, so it should resolve the symlink to the outside path
            # and report it as unsafe.
            is_safe = is_safe_path(symlink_path, root_dir)
            assert is_safe == False, "Symlink to outside directory should be considered unsafe"
        finally:
            os.rmdir(unsafe_target)
