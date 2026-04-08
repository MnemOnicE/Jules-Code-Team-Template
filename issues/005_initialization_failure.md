# Issue 5: Initialization Failure (`ModuleNotFoundError`)

## 1. Objective
Fix the fatal `ModuleNotFoundError` that occurs during the final steps of `template_source/scripts/init_project.py`, ensuring the script exits cleanly and configures the LLM without crashing.

## 2. Context & Problem Statement
During initialization, the `init_project.py` script performs setup steps and then deletes the `template_source/` directory to clean up the repository (Step 6).
Immediately after this cleanup (Step 7.5), the script attempts to dynamically import and configure the LLM provider using:
`from src.core.llm_config import configure_llm_providers`

This approach has two critical flaws:
1. **Integration Mode Failure:** In Integration Mode, the `src` directory is not moved to the root (it stays in `template_source/src` and is skipped). Thus, importing `src` will always fail, regardless of execution order.
2. **Zero-Dependency Violation:** `init_project.py` has a strict 'ZERO-DEPENDENCY' constraint. Importing `src.core.llm_config` violates this, as that module depends on PyYAML and python-dotenv.

Reference: `PLAYTEST.md` and PR Review Feedback.

## 3. Scope of Work
*   **Target:** `template_source/scripts/init_project.py`.
*   **Goal:** Execute the LLM configuration using an isolated subprocess to prevent dependency leakage and to dynamically handle varying source code locations.

## 4. Execution Instructions

**Phase 1: Implement Subprocess Execution**
1. Review `template_source/scripts/init_project.py`, specifically Step 7.5.
2. Remove the dynamic `import` statement.
3. Spawn the LLM configuration as a separate process. This isolates dependencies.
```python
import subprocess
import sys

# Ensure you dynamically resolve the correct path to llm_config based on the environment
# (e.g., if Issue #1 is complete, it will be in .agents/engine/core/llm_config.py)
subprocess.run([sys.executable, "-c", "from core.llm_config import configure_llm_providers; configure_llm_providers()"], check=True)
```

**Phase 2: Dependency Handling**
1. Ensure `init_project.py` gracefully handles the scenario where standard LLM SDK dependencies (`google-genai`, `openai`, `pyyaml`) are missing in the subprocess.
2. Wrap the subprocess call in a `try...except subprocess.CalledProcessError` block. Provide a helpful instruction to the user (e.g., "Skipping LLM config: missing dependencies. Run `pip install -r requirements.txt`") rather than crashing the initialization script.

**Phase 3: Test & Verify**
1. Run `python template_source/scripts/init_project.py`.
2. Ensure the script completes 100% of its steps without throwing a Python stack trace.
3. Verify the final print statement ("Brain: Initializing memory systems...") is reached and executed.

## 5. Definition of Done
* `init_project.py` completes execution entirely.
* Missing LLM SDKs result in a graceful warning, not a fatal crash.
* The script respects the zero-dependency constraint and succeeds in both Greenfield and Integration modes.
