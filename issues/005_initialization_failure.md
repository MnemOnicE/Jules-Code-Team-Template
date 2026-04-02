# Issue 5: Initialization Failure (`ModuleNotFoundError`)

## 1. Objective
Fix the fatal `ModuleNotFoundError` that occurs during the final steps of `template_source/scripts/init_project.py`, ensuring the script exits cleanly and configures the LLM without crashing.

## 2. Context & Problem Statement
During initialization, the `init_project.py` script performs setup steps and then deletes the `template_source/` directory to clean up the repository (Step 6).
Immediately after this cleanup (Step 7.5), the script attempts to dynamically import and configure the LLM provider using:
`from src.core.llm_config import configure_llm_providers`

If the script is running in "Integration Mode" (where the extraction of `src/` is skipped), or if the Python process hasn't re-evaluated its system paths, this import fails catastrophically with `ModuleNotFoundError: No module named 'src'`.

Reference: `PLAYTEST.md`.

## 3. Scope of Work
*   **Target:** `template_source/scripts/init_project.py`.
*   **Goal:** Reorder operations so the LLM configuration occurs *before* cleanup, or execute the configuration in an isolated subprocess that accurately reflects the new environment state.

## 4. Execution Instructions

**Phase 1: Reorder Operations (Preferred Solution)**
1. Review `template_source/scripts/init_project.py`.
2. Move Step 7.5 (LLM Configuration) to occur *before* Step 6 (Cleanup).
3. Ensure that the Python `sys.path` allows the import of `src.core.llm_config` at the time it is executed (which it should, since `template_source` still exists and the root is in the path).

**Alternative/Phase 2 (Subprocess approach, if necessary)**
If moving the step breaks other logic, the LLM configuration can be spawned as a separate process:
```python
import subprocess
import sys

# Instead of dynamic import
subprocess.run([sys.executable, "-c", "from src.core.llm_config import configure_llm_providers; configure_llm_providers()"], check=True)
```
*(Note: If Issue #1 "The Hidden Engine Refactor" is completed, this import path will change to `.agents.engine...`, which must be taken into account.)*

**Phase 3: Dependency Handling**
1. Ensure `init_project.py` gracefully handles the scenario where standard LLM SDK dependencies (`google-genai`, `openai`) are missing.
2. Wrap the configuration call in a `try...except ImportError` block. Provide a helpful instruction to the user (e.g., "Skipping LLM config: missing dependencies. Run `pip install -r requirements.txt`") rather than crashing the script.

**Phase 4: Test & Verify**
1. Run `python template_source/scripts/init_project.py`.
2. Ensure the script completes 100% of its steps without throwing a Python stack trace.
3. Verify the final print statement ("Brain: Initializing memory systems...") is reached and executed.

## 5. Definition of Done
* `init_project.py` completes execution entirely.
* Missing LLM SDKs result in a graceful warning, not a fatal crash.
* The script succeeds in both Greenfield and Integration modes.
