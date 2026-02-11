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
        try:
            v_index = docker_cmd.index("-v")
            mount_arg = docker_cmd[v_index + 1]
            self.assertTrue(mount_arg.endswith(":ro"), f"Volume mount should be read-only. Got: {mount_arg}")
        except (ValueError, IndexError):
            self.fail("'-v' flag for volume mount not found or malformed.")

        # 2. Check other security flags by pairing them up
        cmd_pairs = list(zip(docker_cmd, docker_cmd[1:]))
        self.assertIn(("--network", "none"), cmd_pairs, "Network should be disabled")
        self.assertIn(("--cap-drop", "ALL"), cmd_pairs, "All capabilities should be dropped")
        self.assertIn(("--security-opt", "no-new-privileges"), cmd_pairs, "No new privileges should be allowed")
        self.assertIn(("--tmpfs", "/tmp"), cmd_pairs, "A tmpfs for /tmp should be provided")

if __name__ == "__main__":
    unittest.main()
