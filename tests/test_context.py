import pytest
from unittest.mock import patch, mock_open
import os
import sys

# Import the module to test
from core.context import ContextLoader, load_context

# Fixture to reset the global singleton
@pytest.fixture(autouse=True)
def reset_global_loader():
    """Resets the global _SHARED_LOADER before and after each test."""
    import core.context
    core.context._SHARED_LOADER = None
    yield
    core.context._SHARED_LOADER = None

@pytest.fixture
def mock_fs():
    """
    Mock filesystem operations (exists, open).
    Does NOT mock os.path functions to avoid breaking logic.
    """
    with patch("os.path.exists") as mock_exists, \
         patch("builtins.open", new_callable=mock_open) as mock_file:
        yield {
            "exists": mock_exists,
            "open": mock_file
        }

# --- Tests for _find_root ---


def test_find_root_logic():
    """Test that _find_root correctly navigates up four levels from the file location as a fallback."""
    # We mock __file__ in the module where ContextLoader is defined
    mock_file_path = "/usr/local/src/project/.agents/engine/core/context.py"

    with patch("core.context.__file__", mock_file_path), \
         patch("pathlib.Path.exists", return_value=False), \
         patch.object(ContextLoader, '_find_agents_dir', return_value="/mock/agents"):
                loader = ContextLoader()
                # Calculate what we expect based on the mocked file path fallback:
                # /usr/local/src/project/.agents/engine/core/context.py
                # parents[0]: core
                # parents[1]: engine
                # parents[2]: .agents
                # parents[3]: project
                assert loader.root_dir == "/usr/local/src/project"


# --- Tests for _find_agents_dir ---

def test_find_agents_dir_production_layout(mock_fs):
    """Test finding .agents in the root directory (Production)."""
    mock_root = "/mock/root"
    mock_exists = mock_fs["exists"]

    with patch.object(ContextLoader, '_find_root', return_value=mock_root):
        # Setup: root/.agents exists
        mock_exists.side_effect = lambda path: path == os.path.join(mock_root, '.agents')

        loader = ContextLoader()
        assert loader.agents_dir == os.path.join(mock_root, '.agents')
        mock_exists.assert_called_once_with(os.path.join(mock_root, '.agents'))

def test_find_agents_dir_development_layout(mock_fs):
    """Test finding .agents in template_source (Development)."""
    mock_root = "/mock/root"
    mock_exists = mock_fs["exists"]
    from unittest.mock import call

    with patch.object(ContextLoader, '_find_root', return_value=mock_root):
        # Setup: root/.agents missing, template_source/.agents exists
        mock_exists.side_effect = [False, True]

        loader = ContextLoader()
        assert loader.agents_dir == os.path.join(mock_root, 'template_source', '.agents')

        expected_calls = [
            call(os.path.join(mock_root, '.agents')),
            call(os.path.join(mock_root, 'template_source', '.agents'))
        ]
        mock_exists.assert_has_calls(expected_calls)
        assert mock_exists.call_count == 2

def test_find_agents_dir_missing(mock_fs):
    """Test FileNotFoundError when .agents directory is missing in both locations."""
    mock_root = "/mock/root"
    mock_exists = mock_fs["exists"]
    from unittest.mock import call

    with patch.object(ContextLoader, '_find_root', return_value=mock_root):
        mock_exists.return_value = False

        with pytest.raises(FileNotFoundError, match="Could not locate .agents configuration directory"):
            ContextLoader()

        expected_calls = [
            call(os.path.join(mock_root, '.agents')),
            call(os.path.join(mock_root, 'template_source', '.agents'))
        ]
        mock_exists.assert_has_calls(expected_calls)
        assert mock_exists.call_count == 2

# --- Tests for load_persona ---

def test_load_persona_success(mock_fs):
    """Test loading a persona successfully."""
    mock_agents_dir = "/mock/agents"
    agent_name = "TestAgent"
    expected_content = "# Test Agent Persona"

    # Setup mocks
    # mock_fs is a dict return from the fixture

    with patch.object(ContextLoader, '_find_root', return_value="/mock/root"), \
         patch.object(ContextLoader, '_find_agents_dir', return_value=mock_agents_dir):

        loader = ContextLoader()

        # Configure file read
        mock_fs['exists'].return_value = True
        mock_fs['open'].return_value.__enter__.return_value.read.return_value = expected_content

        content = loader.load_persona(agent_name)
        assert content == expected_content

        # Verify path
        expected_path = os.path.join(mock_agents_dir, 'config', f'{agent_name.lower()}.md')
        mock_fs['open'].assert_called_with(expected_path, 'r', encoding='utf-8')

def test_load_persona_missing(mock_fs):
    """Test FileNotFoundError when persona file is missing."""
    mock_agents_dir = "/mock/agents"
    agent_name = "MissingAgent"

    with patch.object(ContextLoader, '_find_root', return_value="/mock/root"), \
         patch.object(ContextLoader, '_find_agents_dir', return_value=mock_agents_dir):

        loader = ContextLoader()

        # Make exists return False for the specific file
        mock_fs['exists'].return_value = False

        with pytest.raises(FileNotFoundError, match="Persona file not found"):
            loader.load_persona(agent_name)

def test_load_persona_caching(mock_fs):
    """Test that load_persona caches results."""
    mock_agents_dir = "/mock/agents"
    agent_name = "CachedAgent"
    expected_content = "Cached Content"

    with patch.object(ContextLoader, '_find_root', return_value="/mock/root"), \
         patch.object(ContextLoader, '_find_agents_dir', return_value=mock_agents_dir):

        loader = ContextLoader()

        # Setup mocks
        mock_fs['exists'].return_value = True
        mock_fs['open'].return_value.__enter__.return_value.read.return_value = expected_content

        # First call
        content1 = loader.load_persona(agent_name)
        assert content1 == expected_content

        # Second call
        content2 = loader.load_persona(agent_name)
        assert content2 == expected_content

        # Verify open was called only once
        assert mock_fs['open'].call_count == 1

@pytest.mark.parametrize(
    "traversal_name, raises_error, expected_sanitized_name",
    [
        # The original test case
        ("../../etc/passwd", False, "passwd"),
        # Edge cases for basename
        ("..", True, None),
        (".", True, None),
        ("", True, None),
        # Other vectors
        ("/etc/passwd", False, "passwd"),
        ("safe_name", False, "safe_name"),
    ]
)
def test_load_persona_path_traversal_prevention(
    mock_fs, traversal_name, raises_error, expected_sanitized_name
):
    """Test that path traversal attempts in agent_name are sanitized or rejected."""
    mock_agents_dir = "/mock/agents"

    with patch.object(ContextLoader, '_find_root', return_value="/mock/root"), \
         patch.object(ContextLoader, '_find_agents_dir', return_value=mock_agents_dir):

        loader = ContextLoader()

        if raises_error:
            with pytest.raises(ValueError, match="Invalid agent name"):
                loader.load_persona(traversal_name)
        else:
            mock_fs['exists'].return_value = True
            mock_fs['open'].return_value.__enter__.return_value.read.return_value = "content"
            loader.load_persona(traversal_name)
            expected_path = os.path.join(
                mock_agents_dir, 'config', f'{expected_sanitized_name}.md'
            )
            mock_fs['open'].assert_called_with(expected_path, 'r', encoding='utf-8')

# --- Tests for load_tech_stack ---

def test_load_tech_stack_success(mock_fs):
    """Test loading tech stack successfully."""
    mock_agents_dir = "/mock/agents"
    expected_content = "# Tech Stack"

    with patch.object(ContextLoader, '_find_root', return_value="/mock/root"), \
         patch.object(ContextLoader, '_find_agents_dir', return_value=mock_agents_dir):

        loader = ContextLoader()

        # Configure file read
        mock_fs['exists'].return_value = True
        mock_fs['open'].return_value.__enter__.return_value.read.return_value = expected_content

        content = loader.load_tech_stack()
        assert content == expected_content

        # Verify path
        expected_path = os.path.join(mock_agents_dir, 'config', 'TECH_STACK.md')
        mock_fs['open'].assert_called_with(expected_path, 'r', encoding='utf-8')

def test_load_tech_stack_missing(mock_fs):
    """Test FileNotFoundError when tech stack file is missing."""
    mock_agents_dir = "/mock/agents"

    with patch.object(ContextLoader, '_find_root', return_value="/mock/root"), \
         patch.object(ContextLoader, '_find_agents_dir', return_value=mock_agents_dir):

        loader = ContextLoader()
        mock_fs['exists'].return_value = False

        with pytest.raises(FileNotFoundError, match="TECH_STACK.md not found"):
            loader.load_tech_stack()

def test_load_tech_stack_caching(mock_fs):
    """Test that load_tech_stack manually caches results."""
    mock_agents_dir = "/mock/agents"
    expected_content = "Cached Stack"

    with patch.object(ContextLoader, '_find_root', return_value="/mock/root"), \
         patch.object(ContextLoader, '_find_agents_dir', return_value=mock_agents_dir):

        loader = ContextLoader()

        # Setup mocks
        mock_fs['exists'].return_value = True
        mock_fs['open'].return_value.__enter__.return_value.read.return_value = expected_content

        # First call
        content1 = loader.load_tech_stack()
        assert content1 == expected_content

        # Second call
        content2 = loader.load_tech_stack()
        assert content2 == expected_content

        # Verify open was called only once
        assert mock_fs['open'].call_count == 1

# --- Tests for build_system_context ---

def test_build_system_context_success():
    """Test building system context with correct structure."""
    agent_name = "TestAgent"
    persona_content = "Persona content"
    tech_stack_content = "Tech Stack content"

    with patch.object(ContextLoader, '_find_root', return_value="/mock/root"), \
         patch.object(ContextLoader, '_find_agents_dir', return_value="/mock/agents"), \
         patch.object(ContextLoader, 'load_persona', return_value=persona_content), \
         patch.object(ContextLoader, 'load_tech_stack', return_value=tech_stack_content):

        loader = ContextLoader()
        context = loader.build_system_context(agent_name)

        assert context['role'] == agent_name
        assert context['persona'] == persona_content
        assert context['tech_stack'] == tech_stack_content
        assert f"{persona_content}\n\n## Technology Stack\n{tech_stack_content}" == context['system_prompt']

def test_build_system_context_caching():
    """Test that build_system_context caches results."""
    agent_name = "CachedContextAgent"
    persona_content = "Persona content"
    tech_stack_content = "Tech Stack content"

    with patch.object(ContextLoader, '_find_root', return_value="/mock/root"), \
         patch.object(ContextLoader, '_find_agents_dir', return_value="/mock/agents"), \
         patch.object(ContextLoader, 'load_persona', return_value=persona_content) as mock_load_persona, \
         patch.object(ContextLoader, 'load_tech_stack', return_value=tech_stack_content) as mock_load_tech:

        loader = ContextLoader()

        # First call
        context1 = loader.build_system_context(agent_name)
        # Second call
        context2 = loader.build_system_context(agent_name)

        assert context1 is context2
        assert mock_load_persona.call_count == 1
        assert mock_load_tech.call_count == 1

# --- Tests for load_context (Global Singleton) ---

def test_load_context_singleton():
    """Test that load_context uses a singleton loader."""
    agent_name = "SingletonAgent"
    expected_context = {"role": agent_name}

    # We patch ContextLoader to return a mock instance
    with patch("core.context.ContextLoader") as MockLoaderClass:
        mock_instance = MockLoaderClass.return_value
        mock_instance.build_system_context.return_value = expected_context

        # First call: should initialize loader
        context1 = load_context(agent_name)
        assert context1 == expected_context
        assert MockLoaderClass.call_count == 1

        # Second call: should reuse loader
        context2 = load_context(agent_name)
        assert context2 == expected_context
        assert MockLoaderClass.call_count == 1
