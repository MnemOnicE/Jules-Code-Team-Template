import os
import logging

logger = logging.getLogger("Axion.SystemTools")

def _enforce_sandbox(target_path: str):
    """
    Ensures the target path is within the project root.
    """
    root_dir = os.getcwd()
    abs_target = os.path.abspath(target_path)

    # Check common path to ensure it's inside root
    if os.path.commonpath([root_dir, abs_target]) != root_dir:
        raise PermissionError(f"Sandboxing Violation: Access to {target_path} denied.")
    return abs_target

def read_file(path: str):
    """Safely reads a file."""
    try:
        safe_path = _enforce_sandbox(path)
        if not os.path.exists(safe_path):
            return {"status": "error", "message": "File not found"}

        with open(safe_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"status": "success", "content": content}
    except Exception as e:
        logger.error(f"read_file failed: {e}")
        return {"status": "error", "message": str(e)}

def write_file(path: str, content: str):
    """Safely writes to a file."""
    try:
        safe_path = _enforce_sandbox(path)
        # Ensure directory exists
        os.makedirs(os.path.dirname(safe_path), exist_ok=True)

        with open(safe_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"status": "success", "message": f"Written to {path}"}
    except Exception as e:
        logger.error(f"write_file failed: {e}")
        return {"status": "error", "message": str(e)}

def run_command(cmd: str):
    """
    Executes a shell command.
    Currently in SAFE/DUMMY mode.
    """
    logger.warning(f"Dummy Command Execution: {cmd}")
    return {"status": "dummy_mode", "output": f"Simulated execution of: {cmd}"}
