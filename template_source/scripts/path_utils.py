import os
from pathlib import Path


def get_repo_root(start_path=None):
    """Returns the repository root containing either .git or template_source/.agents."""
    if start_path is None:
        start_path = Path.cwd()
    else:
        start_path = Path(start_path).resolve()

    # First pass: look for strong indicators (.git or template_source/.agents)
    temp = start_path
    while True:
        if (temp / '.git').is_dir() or (temp / 'template_source' / '.agents').is_dir():
            return str(temp)
        if temp.parent == temp: # Reached root
            break
        temp = temp.parent

    # Second pass: look for production indicator (.agents at root)
    temp = start_path
    while True:
        if (temp / '.agents').is_dir():
            return str(temp)
        if temp.parent == temp: # Reached root
            break
        temp = temp.parent

    return str(start_path)


def get_agents_dir(root=None):
    """Resolves the active .agents directory in production or development mode."""
    root_path = Path(root or get_repo_root())
    prod_path = root_path / '.agents'
    if prod_path.is_dir():
        return str(prod_path)

    dev_path = root_path / 'template_source' / '.agents'
    if dev_path.is_dir():
        return str(dev_path)

    raise FileNotFoundError(
        f"Could not locate .agents configuration directory. Searched: {prod_path}, {dev_path}"
    )


def get_tech_stack_path(root=None):
    return os.path.join(get_agents_dir(root), 'config', 'TECH_STACK.md')


def get_session_json_path(root=None):
    return os.path.join(get_agents_dir(root), 'memory', 'session.json')


def get_agent_config_path(agent_file, root=None):
    return os.path.join(get_agents_dir(root), 'config', agent_file)
