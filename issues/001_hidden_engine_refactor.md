# Issue 1: The "Hidden Engine" Refactor (Trojan Horse Paradox)

## 1. Objective
Relocate the core agent execution engine from the `src/` directory to the `.agents/engine/` directory. This resolves the "Trojan Horse Paradox" identified in the playtest, where Integration Mode preserves a user's existing `src/` directory but fails to install the agent's execution engine.

## 2. Context & Problem Statement
Currently, `template_source/scripts/init_project.py` has a critical architectural flaw when operating in "Integration Mode" (which is triggered when a user initializes the template into an existing repository). In this mode, the script skips unpacking the `src/` directory to protect the user's existing code. However, all of the agent's core execution logic (e.g., `src/core/bus.py`, `src/core/tools/`, `src/main.py`) resides in this directory.

As a result, the initialized project is left with configuration files in `.agents/config/` but **no execution engine**, rendering the agent completely non-functional.

Reference: `_meta/ARCHITECTURE_CRISIS.md` and `PLAYTEST.md`.

## 3. Scope of Work
*   **Target:** `template_source/src/`, `template_source/scripts/init_project.py`, `pytest.ini`, and all files referencing `src.core`.
*   **Goal:** Move the execution engine to `.agents/engine/` so it is safely isolated from the user's application code, ensuring it installs correctly in both "Greenfield" and "Integration" modes.

## 4. Execution Instructions

**Phase 1: Code Relocation**
1. Move the contents of `template_source/src/` (or specific engine components) to `template_source/.agents/engine/`.
2. Ensure the entry point (e.g., `main.py`) is also relocated or a wrapper script is provided in a standard location (like `scripts/agent.py` or `.agents/engine/main.py`).

**Phase 2: Import Refactoring**
1. Perform a project-wide search for imports starting with `src.core` (e.g., `from src.core.bus import ...`).
2. Update all imports to reflect the new path structure. Assuming `.agents/engine/` is added to the Python path, these imports should become `from core.bus import ...`.

**Phase 3: Update `init_project.py`**
1. Modify `template_source/scripts/init_project.py` so that the extraction of the engine logic targets `.agents/engine/`.
2. Ensure Integration Mode no longer skips the installation of the execution engine.
3. Update the LLM Configuration step (line ~295) to execute the new module path via an isolated subprocess (see Issue #5 documentation).

**Phase 4: Test & Verify**
1. Update `pytest.ini` to ensure `pythonpath` includes the new `.agents/engine` directory so tests can discover the modules.
2. Run the full test suite (`pytest`) to ensure no import errors exist.
3. Simulate an Integration Mode initialization and verify that the `.agents/engine/` directory is created and populated successfully.

## 5. Definition of Done
* The `src/` directory is no longer required for the agent system to function.
* `init_project.py` successfully installs the agent engine in Integration Mode without overwriting user code.
* All tests pass with the new directory structure, and imports correctly resolve from `core...`.
