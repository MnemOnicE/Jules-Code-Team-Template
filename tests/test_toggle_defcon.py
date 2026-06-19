import pytest
import sys
from unittest.mock import patch

from toggle_defcon import main, BOOM_PATH, BOOM_DISABLED_PATH

@patch('toggle_defcon.os.rename')
@patch('toggle_defcon.os.path.exists')
@patch('sys.argv', ['toggle_defcon.py', '--status', 'emergency'])
def test_emergency_activate(mock_exists, mock_rename, capsys):
    """Test emergency mode activates properly when boom.md exists."""
    mock_exists.side_effect = lambda path: path == BOOM_PATH

    main()

    mock_rename.assert_called_once_with(BOOM_PATH, BOOM_DISABLED_PATH)
    captured = capsys.readouterr()
    assert captured.out.strip() == "🚨 DEFCON 1 ACTIVATED: Boom persona has been disabled (renamed to boom.disabled)."

@patch('toggle_defcon.os.rename')
@patch('toggle_defcon.os.path.exists')
@patch('sys.argv', ['toggle_defcon.py', '--status', 'emergency'])
@patch('builtins.print')
def test_emergency_already_active(mock_print, mock_exists, mock_rename):
    """Test emergency mode handles case where already active."""
    mock_exists.side_effect = lambda path: path == BOOM_DISABLED_PATH

    main()

    mock_rename.assert_not_called()
    mock_print.assert_called_once_with("ℹ️  System is already in EMERGENCY mode (Boom is disabled).")

@patch('toggle_defcon.os.rename')
@patch('toggle_defcon.os.path.exists')
@patch('sys.argv', ['toggle_defcon.py', '--status', 'emergency'])
@patch('builtins.print')
def test_emergency_error(mock_print, mock_exists, mock_rename):
    """Test emergency mode handles error when neither file exists."""
    mock_exists.return_value = False

    with pytest.raises(SystemExit) as excinfo:
        main()

    assert excinfo.value.code == 1
    mock_rename.assert_not_called()
    mock_print.assert_called_once_with("⚠️  Error: boom.md not found in defaults. Cannot disable.")

@patch('toggle_defcon.os.rename')
@patch('toggle_defcon.os.path.exists')
@patch('sys.argv', ['toggle_defcon.py', '--status', 'normal'])
@patch('builtins.print')
def test_normal_activate(mock_print, mock_exists, mock_rename):
    """Test normal mode activates properly when boom.disabled exists."""
    mock_exists.side_effect = lambda path: path == BOOM_DISABLED_PATH

    main()

    mock_rename.assert_called_once_with(BOOM_DISABLED_PATH, BOOM_PATH)
    mock_print.assert_called_once_with("✅ DEFCON 1 DEACTIVATED: Boom persona restored.")

@patch('toggle_defcon.os.rename')
@patch('toggle_defcon.os.path.exists')
@patch('sys.argv', ['toggle_defcon.py', '--status', 'normal'])
@patch('builtins.print')
def test_normal_already_active(mock_print, mock_exists, mock_rename):
    """Test normal mode handles case where already active."""
    mock_exists.side_effect = lambda path: path == BOOM_PATH

    main()

    mock_rename.assert_not_called()
    mock_print.assert_called_once_with("ℹ️  System is already in NORMAL mode (Boom is active).")

@patch('toggle_defcon.os.rename')
@patch('toggle_defcon.os.path.exists')
@patch('sys.argv', ['toggle_defcon.py', '--status', 'normal'])
@patch('builtins.print')
def test_normal_error(mock_print, mock_exists, mock_rename):
    """Test normal mode handles error when neither file exists."""
    mock_exists.return_value = False

    with pytest.raises(SystemExit) as excinfo:
        main()

    assert excinfo.value.code == 1
    mock_rename.assert_not_called()
    mock_print.assert_called_once_with("⚠️  Error: boom.disabled not found. Cannot restore.")
