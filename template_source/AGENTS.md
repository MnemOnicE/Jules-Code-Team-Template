# AGENTS.md: The Agent Manifesto

## 1. Intent & Purpose
This repository is an **Agentic GitHub Template** designed to operate as a high-assurance, zero-trust engineering environment. It is not just code; it is a **Governance Protocol**.

As an autonomous agent (Brain, Boom, Sentinel, etc.), your primary directive is to facilitate **Vibe Coding** while strictly adhering to **Architectural Integrity** and **Security Hygiene**.

## 2. The Rulebook
This file serves as the high-level system prompt. for granular, tool-specific configurations, coding standards, and linter rules, strictly adhere to the definitions found in:
**`./.agents/`**

*   **`.agents/config/`**: Agent persona definitions.
*   **`.agents/rules/`**: Specific coding rules and workflow constraints.
*   **`.agents/memory/`**: Shared team memory and session logs.

## 3. Definition of Done
No task is complete until:
1.  **Context is Updated**: `AI_MEMORY.md` records new learnings.
2.  **Drift is Checked**: Changes align with `Project_Plan.md`.
3.  **Verification Passes**: All property-based tests in `tests/verification/` pass.
4.  **Architecture is Valid**: No "God Objects" introduced; diagrams updated.
5.  **Security is Enforced**: No secrets in commits; OIDC identity used.

## 4. Operational Protocols
*   **Context First**: Before writing code, read `/.context/` to understand the domain.
*   **Plan Then Act**: Update `Project_Plan.md` or design docs before implementation.
*   **Evidence Over Hallucination**: Use the "Proof" tools (Hypothesis, Formal Specs) to verify logic.

## 5. System Monitoring & Observability

The system includes comprehensive monitoring capabilities to ensure reliability and performance:

### Real-time Metrics
- **Session Tracking**: Monitor agent sessions and task completion
- **LLM Usage**: Track API calls and response quality
- **Error Detection**: Automatic error logging and alerting
- **Performance Monitoring**: Execution time and resource usage

### Health Checks
Run `python scripts/health_check.py` to validate system integrity:
- Directory structure verification
- Dependency validation
- Configuration integrity
- Engine functionality tests

### Status Monitoring
Use `./squad --status` for real-time system status:
- Current health assessment
- Recent activity log
- Performance metrics
- Active session information

## 6. Plugin Architecture

The system supports extensible functionality through a plugin system:

### Plugin Development
Create plugins in `.agents/plugins/` with the following structure:
```python
PLUGIN_INFO = {
    'name': 'Plugin Name',
    'version': '1.0.0',
    'description': 'Plugin functionality',
    'author': 'Developer Name'
}

def on_session_start(task):
    """Hook called when sessions begin"""
    pass

def on_graph_generated(graph_id):
    """Hook called after graph generation"""
    pass

def on_session_complete(graph_id):
    """Hook called when sessions complete"""
    pass
```

### Available Hooks
- `on_session_start(task)`: Session initialization
- `on_graph_generated(graph_id)`: After execution graph creation
- `on_session_complete(graph_id)`: Session completion
- Custom hooks can be added by extending the plugin manager

### Plugin Management
- Automatic discovery and loading
- Error isolation (plugin failures don't affect core system)
- Hot reloading support
- Version management and compatibility checking

## 7. Maintenance & Operations

### Backup & Recovery
- **Automated Backups**: `python scripts/backup_restore.py backup`
- **Selective Restore**: Restore specific configurations or full system
- **Version Control**: Timestamped backups with compression

### System Updates
- **Update Checking**: `python scripts/update.py --check`
- **Safe Updates**: Automatic backup before applying changes
- **Rollback Support**: Restore from backup if update fails

### Troubleshooting
- **Diagnostic Tools**: Comprehensive health checking
- **Log Analysis**: Session logs in `.agents/memory/`
- **Performance Monitoring**: Real-time metrics and alerts
- **Recovery Procedures**: Documented restoration processes
