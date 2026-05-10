# 🚨 Architecture Crisis Report: The "Trojan Horse" Conflict

## 1. Executive Summary

The current repository structure fundamentally violates its own "Integration Mode" promise. The **Agent Execution Engine** (the code that actually runs the agents) is located inside `src/`, but the initialization script explicitly **skips** unpacking `src/` when installing into an existing project.

**Result:** A user adding this template to an existing repo (Integration Mode) receives the configuration files (`.agents/`) but **zero executable code**. The system is dead on arrival.

## 2. The Conflict
### A. The Promise (README.md)

> "All agent logic is hidden in `.agents/`. Your `src/` folder stays clean."

### B. The Reality (File Structure)

The "Brain" and "Nexus" logic resides in:
- `src/main.py` (CLI Entrypoint)
- `src/core/bus.py` (Nexus Bus)
- `src/core/tools/graph_executor.py` (Graph Executor)
- `src/core/context.py` (Context Loader)

### C. The Mechanism (init_project.py)

In **Integration Mode** (when existing files are detected), the script executes:

```python
# For src/ or other scaffold files, SKIP in Migration Mode
if IS_MIGRATION and item in ['src', 'tests', 'package.json', 'requirements.txt']:
    print(f"Brain: Skipping scaffolding file '{item}' (preserving existing).")
    continue
```

## 3. The Consequence

1.  **Genesis Mode (Fresh Install):** Works fine. `src/` is unpacked because no conflict exists.
2.  **Integration Mode (Existing Repo):**
    - `.agents/` is successfully installed/merged.
    - `src/` is **skipped** to protect the user's existing source code.
    - **Outcome:** The user has config files but no `src/main.py` to run them. The "Coding Squad" exists only as Markdown files, with no engine to animate them.

## 4. Proposed Solution: The "Hidden Engine" Refactor

We must decouple the **User's Source Code** (Project Logic) from the **Agent's Execution Engine** (System Logic).

### Recommendation: Move Engine to `.agents/engine/`

Since `.agents/` is already treated as "System Infrastructure" by `init_project.py` (it is always installed/updated), moving the execution logic there solves the distribution problem immediately.

**New Structure:**

```text
.agents/
├── config/       # Personas (User editable)
├── rules/        # Governance (User editable)
├── engine/       # <--- MOVED HERE (System Logic)
│   ├── __init__.py
│   ├── main.py   # New CLI Entrypoint
│   ├── core/
│   │   ├── bus.py
│   │   ├── tools/
│   │   └── ...
└── ...
```

### Execution Strategy: Bypassing Python's Dot-Directory Limitation

Python cannot directly import modules from directories starting with a dot (like `.agents`). We propose a two-part solution:

1.  **Sys.Path Injection in `.agents/engine/main.py`**:

    The new entrypoint must manipulate `sys.path` to allow absolute imports within the engine without referencing the dot-prefixed root.

    ```python
    import sys
    import os
    # Add engine root to path so "import core.bus" works
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    ```

2.  **The CLI Wrapper (`squad`)**:

    Instead of asking users to run complex Python commands, we drop a lightweight shell script `squad` into the root directory during initialization.

    ```bash
    #!/bin/bash
    # Simple wrapper to launch the hidden agent engine
    python3 .agents/engine/main.py "$@"
    ```

**Benefits:**
1.  **True "Drop-in" Capability:** The agent system becomes a self-contained unit that can be dropped into *any* repo without touching `src/`.
2.  **Zero Conflicts:** We never risk overwriting user code in `src/`.
3.  **Clean Architecture:** Fulfills the README's promise that "Agent logic is hidden."
4.  **Simplified UX:** Users just run `./squad --task "Fix bug"`.
