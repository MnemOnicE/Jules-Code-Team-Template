# Issue 3: Pathing Fragility

## 1. Objective
Eliminate hardcoded paths referencing the `template_source/` directory in utility scripts, ensuring they function correctly both during template development and after initialization in a user's repository.

## 2. Context & Problem Statement
Several scripts, most notably `template_source/scripts/validate_stack.py`, contain hardcoded paths that assume the `template_source/` directory will always exist (e.g., `template_source/.agents/config/TECH_STACK.md`).

However, `template_source/scripts/init_project.py` explicitly deletes the `template_source/` directory at the end of its execution to clean up the repository. This permanently breaks scripts like `validate_stack.py` post-initialization, disabling the semantic firewall and other core functionalities.

Reference: `PLAYTEST.md`.

## 3. Scope of Work
*   **Target:** `template_source/scripts/validate_stack.py`, and any other scripts in `template_source/scripts/` that rely on file paths.
*   **Goal:** Implement dynamic path resolution that falls back gracefully between `.agents/` (production) and `template_source/.agents/` (development).

## 4. Execution Instructions

**Phase 1: Implement Dynamic Path Resolution**
1. Review `template_source/scripts/validate_stack.py`.
2. Replace hardcoded paths like `template_source/.agents/config/TECH_STACK.md`.
3. Implement a robust path resolution strategy. A common pattern used elsewhere in the codebase (e.g., `ContextLoader`) is:
   * First, check if `.agents/` exists in the current working directory (Post-init state).
   * If not, fallback to `template_source/.agents/` (Pre-init/Development state).

```python
import os

def get_agents_dir():
    root = os.getcwd()
    prod_path = os.path.join(root, ".agents")
    dev_path = os.path.join(root, "template_source", ".agents")

    if os.path.exists(prod_path):
        return prod_path
    return dev_path

TECH_STACK_PATH = os.path.join(get_agents_dir(), "config", "TECH_STACK.md")
```

**Phase 2: Audit Other Scripts**
1. Search through all scripts in `template_source/scripts/` (Python and Node.js) for the string `template_source`.
2. Apply the same dynamic resolution pattern to any script that erroneously relies on the template folder persisting.
3. Pay special attention to `check_complexity.js` and `smart_ingest.py` to ensure they target the correct root directories.

**Phase 3: Test & Verify**
1. Run `python template_source/scripts/validate_stack.py` in the default repository state (it should succeed).
2. Rename `template_source/.agents` to `.agents` temporarily (simulating post-init) and run the script again; it should successfully find the config and execute.
3. Revert the temporary rename and ensure test suites pass.

## 5. Definition of Done
* `validate_stack.py` operates successfully without crashing when `template_source` is deleted.
* A standardized path-resolution helper or pattern is used across utility scripts.
