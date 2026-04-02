# 🧪 Jules Code Squad - Playtest Report

## 1. Executive Summary
This playtest evaluated the "Jules Code Team Template" by initializing it into a mock repository, running its core scripts, and attempting to execute natural language tasks through the primary agent loop.

The template presents an impressive conceptual framework (dialectic simulation, adversarial agents, Nexus Bus architecture) but currently suffers from critical runtime errors, hardcoded mock implementations, and structural paradoxes that prevent it from functioning as a drop-in tool.

---

## 2. Initialization Experience (`init_project.py`)

**Action:** Initialized the project via `python template_source/scripts/init_project.py`.
**Mode:** System detected existing files and defaulted to **INTEGRATION MODE**.

### Findings:
- ✅ **Persona Configuration:** Successfully wrote dynamic configuration to `.agents/config/` (e.g., setting Governance Mode to Democracy).
- ✅ **Cleanup:** Cleanly removed `template_source` to prevent clutter.
- ❌ **LLM Configuration Failure:** The script threw an exception during the final steps: `ModuleNotFoundError: No module named 'src'`. This occurs because it attempts to import from `src.core.llm_config` (line 295) after `template_source` is deleted and if `src` wasn't created/preserved in integration mode.
- ❌ **The "Trojan Horse" Paradox:** As documented in `_meta/ARCHITECTURE_CRISIS.md`, Integration Mode explicitly skips unpacking `src/`. Because all execution logic lives in `src/`, the initialized project is left with configuration files but **no execution engine**.

---

## 3. Feature Execution (`src/main.py`)

**Action:** Attempted to create a feature using the CLI: `python3 -m src.main --task "Create a simple Python math utility in src/math_utils.py" --llm gemini`.

### Findings:
- ✅ **LLM Integration:** Capable of loading providers dynamically, and successfully instantiated the `GeminiProvider` after installing the `google-genai` dependency.
- ❌ **Static Execution Graph:** The `main.py` entrypoint does not actually call the LLM to generate an execution plan. Instead, it explicitly calls `generate_mock_graph(task_description)` which returns a hardcoded sequence.
- ❌ **Tool Registry Failure:** The static graph attempts to execute a tool called `plan_decomposition`. However, this tool is never registered in `src/core/tools/registry.py`.
- **Result:** The execution engine immediately halts with: `[ERROR] Tool not found: plan_decomposition`. The task cannot be completed.

---

## 4. Documentation, Memory & Tooling Scripts

**Action:** Tested individual utility scripts located in `scripts/`.

### Findings:
- ❌ **Memory Ingestion (`smart_ingest.py`):** Failed with `NameError: name 'DIGEST_PREFIX' is not defined`. The script crashed while attempting to prune old digest files.
- ❌ **Stack Validation (`validate_stack.py`):** Failed to run properly because it hardcodes the path `template_source/.agents/config/TECH_STACK.md`. Since `template_source` is deleted during initialization, the semantic firewall is permanently broken post-init.
- ✅ **Complexity Checks (`check_complexity.js`):** Ran successfully but found 0 `.mmd` files to evaluate.

---

## 5. Summary of Bugs & Annoyances

1. **Illusion of Functionality:** The system does not dynamically generate graphs using an LLM. It relies on a mock graph, which itself is broken because it references non-existent tools.
2. **Pathing Fragility:** Several scripts (`validate_stack.py`) assume `template_source` will exist forever, breaking immediately after the user runs `init_project.py`.
3. **Integration Mode is Fatal:** By protecting the user's existing `src/` directory, Integration Mode ensures the Agent System never installs its own execution engine.
4. **Missing Dependencies:** Running the LLM providers requires installing SDKs (`google-genai`, `openai`) that aren't natively packed or gracefully handled if missing prior to the user noticing the CLI crash.
5. **Runtime Crashes:** Simple undefined variables (`DIGEST_PREFIX`) completely break core utilities like `smart_ingest.py`.

## 6. Playtester Recommendations

1. **Execute the "Hidden Engine" Refactor:** Act immediately on the `ARCHITECTURE_CRISIS.md` proposal to move the execution engine into `.agents/engine/`.
2. **Implement Real LLM Graph Generation:** Replace `generate_mock_graph` with a call to the active LLM provider, instructing it to output a JSON graph conforming to `src/core/schema/execution_graph.json`.
3. **Fix Path Hardcoding:** Ensure scripts like `validate_stack.py` dynamically resolve the `.agents/` path relative to the project root, not `template_source/`.
4. **Patch Script Variables:** Fix the `NameError` in `smart_ingest.py`.
