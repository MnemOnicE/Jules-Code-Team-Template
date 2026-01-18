import os
import logging
import subprocess
import shutil

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
    Executes a shell command in a hardened Docker container.
    """
    if not shutil.which("docker"):
        logger.critical("Docker not found. Execution blocked for security.")
        return {"status": "error", "message": "CRITICAL: Docker not found. Cannot execute command safely."}

    cwd = os.getcwd()
    docker_cmd = [
        "docker", "run", "--rm",
        "-v", f"{cwd}:/app",
        "-w", "/app",
        "python:3.10-slim",
        "/bin/sh", "-c", cmd
    ]

    try:
        logger.info(f"Executing in Sandbox: {cmd}")
        result = subprocess.run(
            docker_cmd,
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode != 0:
            return {"status": "error", "output": result.stderr, "exit_code": result.returncode}

        return {"status": "success", "output": result.stdout}

    except Exception as e:
        logger.error(f"Sandbox execution failed: {e}")
        return {"status": "error", "message": str(e)}
