from unittest.mock import patch
import tempfile
import os
import shutil
from init_project import update_file

def test_update_file_success(tmp_path, monkeypatch):
    """Test successful file update with search and replace."""
    monkeypatch.chdir(tmp_path)
    d = tmp_path / "subdir"
    d.mkdir()
    f = d / "test.txt"
    f.write_text("Hello World\nThis is a test.")

    update_file(str(f), r"World", "Jules")

    assert f.read_text() == "Hello Jules\nThis is a test."

def test_update_file_no_file():
    """Test that the function handles non-existent files gracefully."""
    # Should not raise an exception
    update_file("non_existent_file.txt", r"foo", "bar")

def test_update_file_no_match(tmp_path, monkeypatch):
    """Test that file content remains unchanged if no match is found."""
    monkeypatch.chdir(tmp_path)
    f = tmp_path / "test.txt"
    f.write_text("No match here.")

    update_file(str(f), r"missing", "found")

    assert f.read_text() == "No match here."

def test_update_file_multiline(tmp_path, monkeypatch):
    """Test that re.MULTILINE flag works correctly."""
    monkeypatch.chdir(tmp_path)
    f = tmp_path / "test.txt"
    content = "Line 1\nLine 2\nLine 3"
    f.write_text(content)

    # ^ matches start of line with MULTILINE
    update_file(str(f), r"^Line 2$", "Modified")

    assert f.read_text() == "Line 1\nModified\nLine 3"

def test_update_file_regex_groups(tmp_path, monkeypatch):
    """Test that regex groups can be used in the replacement."""
    monkeypatch.chdir(tmp_path)
    f = tmp_path / "test.txt"
    f.write_text("version: 1.0.0")

    update_file(str(f), r"version: (\d+\.\d+\.\d+)", r"stable: \1")

    assert f.read_text() == "stable: 1.0.0"


@patch('init_project.input')
@patch('init_project.clear_screen')
@patch('init_project.print_header')
def test_dry_run_mode(mock_print_header, mock_clear_screen, mock_input):
    """Test dry run mode exits early without making changes."""
    # Mock user inputs
    mock_input.side_effect = ['TestProject', 'SaaS', 'Democracy', 'Low', 'Y']
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create minimal template structure
        template_dir = os.path.join(temp_dir, 'template_source')
        os.makedirs(template_dir)
        agents_dir = os.path.join(template_dir, '.agents')
        os.makedirs(agents_dir)
        config_dir = os.path.join(agents_dir, 'config')
        os.makedirs(config_dir)
        
        # Create config files
        for config_file in ['brain.md', 'sentinel.md', 'boom.md']:
            with open(os.path.join(config_dir, config_file), 'w') as f:
                f.write("# Config file\n")
        
        # Change to temp directory
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            from init_project import main
            main(dry_run=True)
            
            # Verify no changes were made
            assert os.path.exists(template_dir)  # Template should still exist
            assert not os.path.exists('.agents')  # Should not be moved
            
        finally:
            os.chdir(original_cwd)


@patch('init_project.input')
@patch('init_project.clear_screen')
@patch('init_project.print_header')
@patch('init_project.configure_git_remote')
@patch('init_project.install_git_hooks')
@patch('init_project.subprocess.run')
def test_integration_genesis_mode(mock_subprocess, mock_install_hooks, mock_configure_git, 
                                 mock_print_header, mock_clear_screen, mock_input):
    """Integration test for genesis mode (new project)."""
    # Mock user inputs
    mock_input.side_effect = ['TestProject', 'SaaS', 'Democracy', 'Low', '']  # Empty for git remote
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create template structure
        template_dir = os.path.join(temp_dir, 'template_source')
        os.makedirs(template_dir)
        
        # Create .agents structure
        agents_dir = os.path.join(template_dir, '.agents')
        os.makedirs(agents_dir)
        config_dir = os.path.join(agents_dir, 'config')
        os.makedirs(config_dir)
        
        # Create config files
        for config_file in ['brain.md', 'sentinel.md', 'boom.md']:
            with open(os.path.join(config_dir, config_file), 'w') as f:
                f.write("**Current Mode:** Democracy\n**Role:** Security & Compliance.\n**Role:** Feature Delivery.\n")
        
        # Create other template files
        with open(os.path.join(template_dir, 'README.md'), 'w') as f:
            f.write("# Template README\n")
        
        with open(os.path.join(template_dir, 'squad'), 'w') as f:
            f.write("#!/bin/bash\necho 'squad script'\n")
        
        # Change to temp directory
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            from init_project import main
            with patch('core.llm_config.configure_llm_providers'):
                main()
            
            # Verify initialization
            assert os.path.exists('.agents')  # Agents moved
            assert os.path.exists('README.md')  # README moved
            assert os.path.exists('squad')  # Squad script moved
            assert os.access('squad', os.X_OK)  # Executable
            assert not os.path.exists(template_dir)  # Template cleaned up
            
        finally:
            os.chdir(original_cwd)


@patch('init_project.input')
@patch('init_project.clear_screen')
@patch('init_project.print_header')
def test_integration_migration_mode(mock_print_header, mock_clear_screen, mock_input):
    """Integration test for migration mode (existing project)."""
    # Mock user inputs
    mock_input.side_effect = ['ExistingProject', 'Legacy Codebase', 'Dictator', 'High', '']  # Empty for git remote
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create existing project files
        with open(os.path.join(temp_dir, 'existing_file.py'), 'w') as f:
            f.write("print('existing')\n")
        
        # Create template structure
        template_dir = os.path.join(temp_dir, 'template_source')
        os.makedirs(template_dir)
        
        agents_dir = os.path.join(template_dir, '.agents')
        os.makedirs(agents_dir)
        docs_dir = os.path.join(agents_dir, 'docs')
        os.makedirs(docs_dir)
        config_dir = os.path.join(agents_dir, 'config')
        os.makedirs(config_dir)
        
        # Create config files
        for config_file in ['brain.md', 'sentinel.md', 'boom.md']:
            with open(os.path.join(config_dir, config_file), 'w') as f:
                f.write("**Current Mode:** Democracy\n**Role:** Security & Compliance.\n**Role:** Feature Delivery.\n")
        
        # Create template README
        with open(os.path.join(template_dir, 'README.md'), 'w') as f:
            f.write("# Template Manual\n")
        
        # Create existing README
        with open(os.path.join(temp_dir, 'README.md'), 'w') as f:
            f.write("# Existing Project\n")
        
        # Change to temp directory
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            from init_project import main
            with patch('core.llm_config.configure_llm_providers'):
                main()
            
            # Verify migration
            assert os.path.exists('.agents')  # Agents installed
            assert os.path.exists('existing_file.py')  # Existing file preserved
            assert os.path.exists('README.md')  # Existing README preserved
            assert os.path.exists('.agents/docs/USER_MANUAL.md')  # Manual moved
            assert not os.path.exists(template_dir)  # Template cleaned up
            
        finally:
            os.chdir(original_cwd)


def test_validate_governance():
    """Test governance input validation."""
    from init_project import validate_governance
    
    assert validate_governance("Democracy") == True
    assert validate_governance("dictator") == True
    assert validate_governance("invalid") == False
    assert validate_governance("") == False


def test_validate_risk():
    """Test risk input validation."""
    from init_project import validate_risk
    
    assert validate_risk("High") == True
    assert validate_risk("medium") == True
    assert validate_risk("low") == True
    assert validate_risk("invalid") == False


@patch('init_project.input')
@patch('init_project.clear_screen')
@patch('init_project.print_header')
def test_main_dry_run_already_initialized(mock_print_header, mock_clear_screen, mock_input):
    """Test that main exits early when already initialized."""
    from init_project import main
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # No template_source directory = already initialized
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            main(dry_run=True)
            # Should not raise exception and should exit early
        finally:
            os.chdir(original_cwd)
