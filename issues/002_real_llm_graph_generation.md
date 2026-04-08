# Issue 2: Real LLM Graph Generation

## 1. Objective
Replace the hardcoded mock execution graph in `src/main.py` with an actual call to the configured LLM provider, ensuring the system dynamically generates execution plans based on user input.

## 2. Context & Problem Statement
The current CLI entry point (`src/main.py`) processes user tasks but does not invoke an LLM to generate an execution plan. Instead, it relies on a `generate_mock_graph` function that returns a static, hardcoded JSON sequence.

Furthermore, this mock graph attempts to call an unregistered tool (`plan_decomposition`), causing the execution engine to immediately halt with a `[ERROR] Tool not found: plan_decomposition` message. This breaks the primary user flow and creates an "Illusion of Functionality."

Reference: `PLAYTEST.md`.

## 3. Scope of Work
*   **Target:** `src/main.py` (or its new location after the Hidden Engine refactor), `src/core/tools/registry.py` (optional, if default tools need updating).
*   **Goal:** Connect the initialized LLM provider to the task input and parse its response into a valid Execution Graph.

## 4. Execution Instructions

**Phase 1: Implement LLM Orchestration**
1. Review the CLI entry point (e.g., `main.py`) and locate the `generate_mock_graph` call.
2. Remove the mock function entirely.
3. Utilize the instantiated LLM provider (e.g., `provider = get_provider(...)`) to send a prompt containing the `task_description` and the required JSON schema (`execution_graph.json`).
4. Instruct the LLM to return *only* a JSON object conforming to the schema.
5. **Important:** The path to `execution_graph.json` must be resolved dynamically. After Issue #1 (Hidden Engine Refactor) is completed, this file will reside in `.agents/engine/core/schema/`, not `src/core/schema/`.

**Phase 2: Response Parsing & Validation**
1. Implement robust parsing logic to extract the JSON payload from the LLM's response (handling potential markdown formatting like ```json ... ```).
2. Pass the parsed JSON dictionary to the existing `bus.validate_graph()` and `bus.execute()` pipeline.
3. Ensure proper error handling if the LLM returns invalid JSON or a graph that fails schema validation (e.g., prompting the LLM again for a correction, or failing gracefully).

**Phase 3: Clean up Unregistered Tools**
1. Investigate if the `plan_decomposition` tool mentioned in the mock graph should exist. If it's a legacy concept, ignore it. If it's intended, ensure it is registered in `core/tools/registry.py` or `core/tools/agent_tools.py`.
2. Ensure the initial prompt to the LLM includes a list of *currently available/registered tools* so it knows what actions it can take.

**Phase 4: Test & Verify**
1. Run a simple task via the CLI: `python3 -m src.main --task "List files in the current directory" --llm mock` (assuming a mock provider exists for testing, or use gemini/openai with a real key).
2. Verify the logs show a dynamically generated graph, structural validation passing, and successful execution of the generated nodes.

## 5. Definition of Done
* `generate_mock_graph` is removed.
* The system dynamically calls an LLM, parses the response, and executes a real graph.
* The system dynamically resolves the schema path and handles invalid LLM responses gracefully.
