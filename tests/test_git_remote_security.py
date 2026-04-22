import unittest
from unittest.mock import patch
import sys
import os

# Add template_source/scripts to sys.path to import init_project
sys.path.insert(0, os.path.join(os.getcwd(), 'template_source', 'scripts'))
import init_project

class TestGitRemoteSecurity(unittest.TestCase):
    def test_validate_git_remote_valid(self):
        valid_urls = [
            "https://github.com/user/repo.git",
            "git@github.com:user/repo.git",
            "ssh://git@github.com/user/repo.git",
            "/path/to/local/repo",
            "C:\\path\\to\\repo"
        ]
        for url in valid_urls:
            with self.subTest(url=url):
                self.assertTrue(init_project.validate_git_remote(url))

    def test_validate_git_remote_invalid(self):
        invalid_urls = [
            "--help",
            "-oProxyCommand=touch /tmp/pwned",
            "ext::sh -c touch% /tmp/pwned",
            "EXT::something",
            "  -hyphenated"
        ]
        for url in invalid_urls:
            with self.subTest(url=url):
                self.assertFalse(init_project.validate_git_remote(url))

    @patch('subprocess.run')
    @patch('builtins.input')
    def test_configure_git_remote_execution(self, mock_input, mock_run):
        mock_input.return_value = "https://github.com/user/repo.git"
        init_project.configure_git_remote(is_migration=False)

        # Check if subprocess.run was called correctly
        # The first call is "git remote remove origin", we want the second one
        calls = [call.args[0] for call in mock_run.call_args_list]
        add_call = [c for c in calls if "add" in c][0]
        self.assertEqual(add_call, ["git", "remote", "add", "--", "origin", "https://github.com/user/repo.git"])

    @patch('subprocess.run')
    @patch('builtins.input')
    def test_configure_git_remote_blocks_malicious(self, mock_input, mock_run):
        mock_input.return_value = "--help"
        with patch('builtins.print') as mock_print:
            init_project.configure_git_remote(is_migration=False)
            mock_print.assert_any_call("❌ Security Error: Invalid or dangerous Git remote URL: --help")

        # subprocess.run should not be called with "add"
        calls = [call.args[0] for call in mock_run.call_args_list]
        add_calls = [c for c in calls if "add" in c]
        self.assertEqual(len(add_calls), 0)

if __name__ == '__main__':
    unittest.main()
