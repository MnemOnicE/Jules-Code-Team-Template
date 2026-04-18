# Architecture Crisis: The Hidden Engine Refactor

## Context

During a comprehensive audit of the repository, a significant disconnect was found between the active codebase and its documentation (fossil record). The documentation referenced severe "Environment Fragility" and "Mock Dependency" issues located in a nonexistent `src/` directory.

Through investigation, it was discovered that a "Hidden Engine Refactor" had already taken place. The engine components were moved from the root `src/` directory to `template_source/.agents/engine/`.

## Resolution

The refactor successfully resolved both issues:

1.  **Mock Dependency:** `generate_mock_graph` was completely removed. `template_source/.agents/engine/main.py` now implements a fully functional `generate_llm_graph` method that correctly queries the LLM provider.
2.  **Environment Fragility:** `template_source/.agents/engine/core/context.py` now safely checks the production deployment path `.agents` first, only falling back to `template_source/.agents` in local development mode. This prevents runtime crashes in deployed systems.

## Status

**RESOLVED.** The documentation has been synchronized with physical reality. The codebase is structurally sound.
