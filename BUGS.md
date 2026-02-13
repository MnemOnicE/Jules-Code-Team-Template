# 🐛 Known Issues & Audit Findings

## Code Health
- [ ] **Inconsistent Error Handling**: `src/core/tools/system.py` raises `PermissionError` in `_enforce_sandbox` but returns an error dictionary in `read_file`. This inconsistency should be resolved.
- [ ] **Hardcoded Logic**: `src/main.py` contains a hardcoded `generate_mock_graph` function which serves as a placeholder. This should ideally be moved to a test utility or mock factory.
- [ ] **Logging Strategy**: `src/core/bus.py` uses `print()` statements for validation and execution logs. It should use the `logging` module consistent with other parts of the system (e.g., `src/core/tools/registry.py`).
- [ ] **Missing Tests**: `src/core/tools/system.py` lacks unit tests for `_enforce_sandbox` and `read_file`.

## Documentation
- [ ] **README.md Usage**: The `README.md` lacks instructions on how to run the agent system directly via `src/main.py` (e.g., `python -m src.main --task "..."`).
- [ ] **Architecture Diagram**: The Mermaid diagram in `README.md` depicts a high-level conceptual flow but does not reflect the actual class structure (`NexusBus`, `GraphExecutor`, `ToolRegistry`).
- [ ] **Missing Reference**: The `README.md` refers to `smart_ingest.py` as if it's a core feature available to the user, but it's located in `template_source/scripts/`.

## Functional
- [ ] **Schema Validation**: `src/core/bus.py` raises `jsonschema.ValidationError` directly. It might be better to catch this and return a structured error response, or at least log it properly.
- [ ] **Context Loading**: `src/core/context.py` correctly falls back to `template_source/.agents`, but this dependency on `template_source` from `src` (the production code) is unusual. Typically `src` should be standalone after initialization.

## Future Improvements
- [ ] **Refactor `generate_mock_graph`**: Move this logic to a dedicated `tests/mocks/graph_factory.py`.
- [ ] **Standardize Returns**: Ensure all tool functions return a consistent dictionary format (e.g., `{"status": "...", "data": ...}`).
