import os
from pathlib import Path


def get_repo_root(start_path=None):
    """Returns the repository root containing either .git or template_source/.agents."""
    if start_path is None:
        start_path = os.getcwd()

    current = Path(start_path).resolve()
    for parent in [current] + list(current.parents):
        if (parent / '.git').exists():
            return str(parent)
        if (parent / '.agents').exists() or (parent / 'template_source' / '.agents').exists():
            return str(parent)
    return str(current)


def get_agents_dir(root=None):
    """Resolves the active .agents directory in production or development mode."""
    root = Path(root or get_repo_root())
    prod_path = root / '.agents'
    if prod_path.exists():
        return str(prod_path)

    dev_path = root / 'template_source' / '.agents'
    if dev_path.exists():
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
