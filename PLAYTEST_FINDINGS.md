# Playtest Findings: Initial Project Template

During the automated playtest of the template utilizing real user interactions, the following issues and observations were recorded:

## Initialization Phase (`init_project.py`)

1. **Missing Dependencies for Initialization Script:**
   - The script `init_project.py` tries to import `yaml` but fails because `PyYAML` and `python-dotenv` are not installed by default in the environment before `init_project.py` executes them. A workaround was to manually run `pip install PyYAML python-dotenv` before running the initialization, which breaks the promised zero-dependency start.

2. **Gitingest Missing Error:**
   - At the end of the initialization flow, there is a critical failure notice: `❌ CRITICAL: gitingest not found. Memory updates disabled. Please install via pip.` This creates a suboptimal onboarding experience. The initialization should probably auto-install this or handle the absence more gracefully since the user is not warned about this requirement.

## Runtime Phase (`./squad` Wrapper)

1. **Missing `jsonschema` Dependency:**
   - When attempting to run the engine for the first time via `./squad`, the script immediately failed with `Error importing modules: No module named 'jsonschema'`. The dependency is missing from the required setup sequence.

2. **Hardcoded Directory Assumptions in `core/context.py`:**
   - The `ContextLoader` has a method `_find_root()` which heavily relies on the execution happening from `src/core/context.py`. When running the `squad` command, the `ContextLoader` assumes the `.agents` folder is in a specific hierarchical structure that no longer aligns with how the squad wrapper invokes `main.py` directly from `.agents/engine/main.py`. This caused a `FileNotFoundError` when trying to locate the persona configuration files. A manual code patch in `context.py` was needed to continue.

3. **Method Signature Mismatch in `core/main.py`:**
   - Inside `generate_llm_graph()`, `provider.generate(prompt)` is called. However, the abstract `LLMProvider.generate()` requires two arguments: `system_prompt` and `user_prompt`. This mismatch throws a `TypeError: GeminiProvider.generate() missing 1 required positional argument: 'user_prompt'` preventing graph generation.

4. **API Limits Hit:**
   - During the Gemini execution test, the API key provided quickly threw a `429 RESOURCE_EXHAUSTED` error due to free-tier limits being hit. Though this is specific to the API key rather than a code defect, it highlights that rate-limit handling and graceful retries/fallback might be needed for the LLM Provider integration to survive quota bumps seamlessly.

## General Observations
- The interactive prompts worked well in detecting "Integration Mode" correctly based on the directory contents.
- The Git endpoint security bypass for "Integration Mode" works correctly.

## Recommendations for Fixes:
- Adjust init_project.py to ensure PyYAML, python-dotenv, and gitingest are installed via subprocess (followed by importlib.invalidate_caches()) before attempting imports or execution loops.
- Add `jsonschema` to the list of core dependencies installed during the template initialization.
- Refactor ContextLoader._find_root() in context.py to correctly calculate the root directory robustly and fix the persona path mismatch (init_project.py uses config/ while context.py expects config/defaults/).
- Fix the `generate()` method call inside `main.py` to pass the correct arguments matching the `LLMProvider` signature (e.g., passing `""` for system prompt if only one is meant to be sent).
