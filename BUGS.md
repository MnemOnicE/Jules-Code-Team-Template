# 🐛 Known Issues & Audit Findings

## Code Health
- [ ] **Logging Strategy**: `src/core/bus.py` uses `print()` statements for validation and execution logs. It should use the `logging` module consistent with other parts of the system (e.g., `src/core/tools/registry.py`).

## Documentation
- [ ] **README.md Usage**: The `README.md` lacks instructions on how to run the agent system directly via `src/main.py` (e.g., `python -m src.main --task "..."`).
- [ ] **Architecture Diagram**: The Mermaid diagram in `README.md` depicts a high-level conceptual flow but does not reflect the actual class structure (`NexusBus`, `GraphExecutor`, `ToolRegistry`).
- [ ] **Missing Reference**: The `README.md` refers to `smart_ingest.py` as if it's a core feature available to the user, but it's located in `template_source/scripts/`.

## Functional
- [ ] **Schema Validation**: `src/core/bus.py` raises `jsonschema.ValidationError` directly. It might be better to catch this and return a structured error response, or at least log it properly.

## Future Improvements
- [ ] **Standardize Returns**: Ensure all tool functions return a consistent dictionary format (e.g., `{"status": "...", "data": ...}`).
