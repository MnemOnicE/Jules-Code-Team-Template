# ⌨️ Agent Command Interface (CLI)

The user may invoke these commands at the start of a prompt to trigger specific workflows immediately.

## Agent Commands

| Command | Workflow Trigger | Description |
| :--- | :--- | :--- |
| **/standup** `[topic]` | `workflows/standup.md` | **Brain** convenes the squad to debate architecture or features. |
| **/judge** `[code]` | `workflows/code_review.md` | **The Code Court.** Triggers Sentinel, Bolt, and Scribe to review input code. |
| **/test** | `workflows/qa.md` | **Scope's Gauntlet.** Generates 3 edge cases to break the current feature. |
| **/panic** | `workflows/incident.md` | **The War Room.** Bypasses debate. Fixes critical bugs immediately. |
| **/reflect** | `.agents/memory/TEAM_MEMORY.md` | **Scribe** forces a memory commit. Summarizes the session into the permanent log. |
| **/refresh** | `workflows/refresh.md` | **Brain** manually triggers the ingestion script to update context. |
| **/status** | `.agents/memory/ROADMAP.md` | **Brain** reports current active task and next planned items. |
| **/audit** | `workflows/audit.md` | **Brain** performs a full repository state analysis (Blueprint, Debt, Status, Reflect). |
| **/auto** | `workflows/autopilot.md` | **The Scout.** Brain scans the Roadmap and Memory to find the next best task automatically. |
| **/refactor** `[file]` | `workflows/refactor.md` | **The Janitor.** Bolt and Scribe clean up code without changing logic. |
| **/ship** `[ver]` | `workflows/release.md` | **The Release Manager.** Prepares changelogs and verifies builds. |
| **/explain** `[file]` | `workflows/explain.md` | **The Teacher.** Adds comments and explains complex logic. |
| **/design** `[idea]` | `workflows/design.md` | **The Architect.** Generates technical specs in `specs/` before coding. |
| **/heal** `[log]` | `workflows/heal.md` | **The Medic.** Autonomously diagnoses and patches errors. |
| **/manage** `[goal]` | `workflows/conductor.md` | **The Conductor.** Chains multiple protocols to solve complex goals. |
| **/sidebar** | `N/A` | **Break Character.** Drops all personas to answer queries directly and concisely. No logs. |

## System Management Commands

| Command | Description |
| :--- | :--- |
| **`./squad --status`** | Show real-time system metrics and recent activity |
| **`./squad --config-llm`** | Configure or reconfigure LLM providers |
| **`./squad --help`** | Display all available command-line options |

## Utility Scripts

| Script | Purpose | Usage |
| :--- | :--- | :--- |
| **`scripts/health_check.py`** | System diagnostics | `python scripts/health_check.py` |
| **`scripts/backup_restore.py`** | Configuration backup/restore | `python scripts/backup_restore.py backup` |
| **`scripts/update.py`** | System updates | `python scripts/update.py --check` |
| **`scripts/init_project.py`** | System initialization | `python scripts/init_project.py --dry-run` |

## Command-Line Options

The main engine supports various options for advanced usage:

```bash
./squad --task "Build a user authentication system"
./squad --file path/to/code.py
./squad --llm openai --model-path gpt-4
./squad --raw-send --raw-return  # Debug LLM communication
./squad --status                 # System health and metrics
./squad --config-llm            # LLM provider setup
```

## Plugin System

The system supports plugins for extending functionality. Plugins are loaded from `.agents/plugins/` and can hook into various system events:

- `on_session_start(task)` - Called when a session begins
- `on_graph_generated(graph_id)` - Called after graph generation
- `on_session_complete(graph_id)` - Called when a session ends

Plugins must include `PLUGIN_INFO` metadata and may be restricted by `.agents/plugins/allowed_plugins.json`.

If an allowlist file exists, only listed plugin names are permitted to load. A plugin entry may also include a `hash` field to verify the plugin file integrity using SHA-256.

Example plugin structure:
```python
PLUGIN_INFO = {
    'name': 'My Plugin',
    'version': '1.0.0',
    'description': 'Custom functionality',
    'author': 'Your Name'
}

def on_session_start(task):
    print(f"Plugin activated for: {task}")
```

Example allowlist:
```json
{
  "plugins": {
    "metrics": {
      "hash": "<sha256-of-metrics.py>"
    }
  }
}
```
