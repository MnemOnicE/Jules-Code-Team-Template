# 🛠️ System Utilities Documentation

This document covers the utility scripts and tools available in the Jules Code Team system for maintenance, monitoring, and management.

## Health Check (`scripts/health_check.py`)

Comprehensive system diagnostics tool that validates the integrity of your Jules Code Team installation.

### Usage
```bash
python scripts/health_check.py
```

### What It Checks
- **Directory Structure**: Verifies `.agents/` directory and subdirectories exist
- **Core Dependencies**: Validates required Python modules (yaml, dotenv, jsonschema)
- **Agent Configurations**: Ensures essential config files are present
- **Engine Integrity**: Tests main engine module loading and syntax

### Output
- ✅ **Green indicators** for healthy components
- ❌ **Red indicators** for failed checks with detailed error messages
- 📋 **Actionable recommendations** for fixing issues

### Exit Codes
- `0`: All checks passed
- `1`: One or more checks failed

## Backup & Restore (`scripts/backup_restore.py`)

Safely backup and restore your agent configurations, memory, and customizations.

### Backup Command
```bash
# Create a new backup
python scripts/backup_restore.py backup

# Create backup with custom name
python scripts/backup_restore.py backup --file my_backup.tar.gz
```

**What Gets Backed Up:**
- `.agents/config/` - Agent personalities and settings
- `.agents/memory/` - Session logs and learned knowledge
- `.agents/rules/` - Custom coding standards
- `AI_MEMORY.md` - Project knowledge base
- `session.json` - Current session state

### Restore Command
```bash
# List available backups
python scripts/backup_restore.py list

# Restore from backup
python scripts/backup_restore.py restore --file agents_backup_20260407_120000.tar.gz

# Force restore (overwrite existing files)
python scripts/backup_restore.py restore --file backup.tar.gz --force
```

### Safety Features
- **Automatic timestamps** for backup files
- **Confirmation prompts** before destructive operations
- **Compression** to save disk space
- **Selective restoration** to preserve existing work

## Update System (`scripts/update.py`)

Keep your Jules Code Team system current with the latest features and fixes.

### Check for Updates
```bash
python scripts/update.py --check
```

Shows available updates and version information.

### Apply Updates
```bash
# Apply latest updates
python scripts/update.py --apply

# Preview what would be updated
python scripts/update.py --apply --dry-run

# Update to specific version
python scripts/update.py --apply --version v1.2.0
```

### Update Process
1. **Version Check**: Compares current vs latest versions
2. **Backup Creation**: Automatically backs up current state
3. **Safe Update**: Downloads and applies updates
4. **Verification**: Runs health checks post-update
5. **Rollback Ready**: Backup available if issues occur

## Initialization Script (`scripts/init_project.py`)

Enhanced project initialization with comprehensive options and validation.

### Basic Usage
```bash
# Interactive initialization
python scripts/init_project.py

# Preview changes without applying
python scripts/init_project.py --dry-run

# Force initialization (override safety checks)
python scripts/init_project.py --force
```

### Features
- **Migration Detection**: Automatically detects existing projects
- **Input Validation**: Validates governance and risk tolerance choices
- **Configuration Summary**: Shows settings before applying
- **Progress Feedback**: Clear status updates during initialization
- **Error Recovery**: Comprehensive error handling and cleanup

### Modes
- **Genesis Mode**: For new projects (creates full structure)
- **Integration Mode**: For existing projects (adds agents without overwriting)

## Monitoring & Status (`./squad --status`)

Real-time system monitoring and performance metrics.

### Usage
```bash
./squad --status
```

### Metrics Displayed
- **System Health**: Overall status (good/warning/critical)
- **Session Count**: Total sessions started
- **LLM Calls**: API calls made to language models
- **Error Count**: Failed operations
- **Recent Events**: Last 10 system events with timestamps

### Event Types
- `session_start`: New session initiated
- `llm_provider_ready`: LLM configured successfully
- `graph_generated`: Execution graph created
- `session_complete`: Session finished successfully

## Plugin System

### Overview
The plugin system allows extending Jules Code Team functionality without modifying core code.

### Plugin Location
```
.agents/plugins/
├── example_plugin.py
└── my_custom_plugin.py
```

### Plugin Structure
```python
# Required: Plugin metadata
PLUGIN_INFO = {
    'name': 'My Plugin',
    'version': '1.0.0',
    'description': 'What this plugin does',
    'author': 'Your Name'
}

# Optional: Hook functions
def on_session_start(task):
    """Called when a session begins"""
    print(f"Plugin activated for: {task}")

def on_graph_generated(graph_id):
    """Called after graph generation"""
    print(f"Graph created: {graph_id}")

def on_session_complete(graph_id):
    """Called when session ends"""
    print(f"Session finished: {graph_id}")
```

### Plugin Management
- **Automatic Loading**: Plugins in `.agents/plugins/` load on startup
- **Error Isolation**: Plugin failures don't affect core system
- **Hot Reloading**: Restart engine to load plugin changes

## Troubleshooting

### Common Issues

**Health Check Fails**
```bash
# Run detailed diagnostics
python scripts/health_check.py

# Check Python path
python -c "import sys; print(sys.path)"
```

**Backup/Restore Issues**
```bash
# Verify permissions
ls -la .agents/

# Check disk space
df -h
```

**Update Problems**
```bash
# Manual backup before update
python scripts/backup_restore.py backup

# Check network connectivity
curl -I https://api.github.com
```

**Plugin Loading Errors**
```bash
# Validate plugin syntax
python -m py_compile .agents/plugins/my_plugin.py

# Check plugin structure
python -c "import importlib.util; spec = importlib.util.spec_from_file_location('test', '.agents/plugins/my_plugin.py'); print('Valid' if spec else 'Invalid')"
```

### Getting Help
- Run `python scripts/health_check.py` for system diagnostics
- Use `./squad --status` for real-time monitoring
- Check `.agents/memory/session.json` for detailed logs
- Create backups before major operations

## Best Practices

### Regular Maintenance
```bash
# Weekly health checks
python scripts/health_check.py

# Monthly backups
python scripts/backup_restore.py backup

# Check for updates regularly
python scripts/update.py --check
```

### Before Major Changes
1. Create backup: `python scripts/backup_restore.py backup`
2. Run health check: `python scripts/health_check.py`
3. Apply changes
4. Verify: `python scripts/health_check.py`

### Plugin Development
- Test plugins in isolation before deployment
- Use descriptive names and versions
- Handle errors gracefully in hook functions
- Document plugin functionality clearly