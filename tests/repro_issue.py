import unittest
from unittest.mock import patch, MagicMock
import os
import shutil
import sys

# Ensure src is in path
sys.path.append(os.getcwd())

from src.core.tools.system import run_command

class TestRunCommandSecurity(unittest.TestCase):
    @patch("shutil.which")
    @patch("subprocess.run")
    @patch("os.getcwd")
    def test_run_command_security_flags(self, mock_getcwd, mock_run, mock_which):
        # Setup
        mock_which.return_value = "/usr/bin/docker"
        mock_getcwd.return_value = "/home/user/project"
        mock_run.return_value = MagicMock(returncode=0, stdout="success", stderr="")

        cmd = "ls -l"
        run_command(cmd)

        # Capture the call to subprocess.run
        self.assertTrue(mock_run.called)
        docker_cmd = mock_run.call_args[0][0]

        # Verify security flags

        # 1. Volume mount should be read-only
        mount_arg = ""
        for i, arg in enumerate(docker_cmd):
            if arg == "-v":
                mount_arg = docker_cmd[i+1]
                break

        self.assertTrue(mount_arg.endswith(":ro"), f"Volume mount should be read-only. Got: {mount_arg}")

        # 2. Network should be disabled
        self.assertIn("--network", docker_cmd)
        self.assertIn("none", docker_cmd)

        # 3. Capabilities should be dropped
        self.assertIn("--cap-drop", docker_cmd)
        self.assertIn("ALL", docker_cmd)

        # 4. No new privileges
        self.assertIn("--security-opt", docker_cmd)
        self.assertIn("no-new-privileges", docker_cmd)

if __name__ == "__main__":
    unittest.main()
