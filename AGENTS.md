## 📚 Repository Context

This repository uses an automated ingestion system to maintain a snapshot of the codebase history.
Agents should check the `ingests/` directory for the latest codebase digest file (e.g., `digest_YYYYMMDD_HHMMSS.txt`).
Reading this file provides a comprehensive understanding of the project's state, structure, and content at that point in time.

The ingestion process is managed by `template_source/scripts/smart_ingest.py`, which is designed to run every 5 commits (or when the directory is empty), keeping only the latest 3 snapshots. It can also be forced via the `--force` flag for manual or emergency updates.

## 🛠️ System Architecture

The core runtime environment is located in `src/`, designed to be the "Active Core" of the agent instance.

### Key Components
- **`src/main.py`**: The CLI entry point. Initializes the `NexusBus` and `GraphExecutor`.
- **`src/core/bus.py`**: The **Nexus Bus**. Handles event dispatching and validates execution graphs against `src/core/schema/execution_graph.json`.
- **`src/core/tools/graph_executor.py`**: The **Graph Executor**. Traverses the graph, executes nodes, and manages the retry/repair loop.
- **`src/core/context.py`**: The **Context Loader**. Loads agent personas (`.agents/config/defaults/*.md`) and the tech stack (`TECH_STACK.md`).
- **`src/core/tools/registry.py`**: The **Tool Registry**. Maps string identifiers in the graph to Python functions.

## ⚠️ Known Issues

Please refer to `BUGS.md` for a current list of known code health issues and architectural discrepancies.
