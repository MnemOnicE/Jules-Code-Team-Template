# Jules Code Team Template

**AI-Powered Software Development Environment**

This project provides a comprehensive, autonomous coding assistant system that transforms how you build software. The Jules Code Team combines multiple AI agents working together to handle everything from architecture design to code implementation, testing, and deployment.

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](/LICENSE)
![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)
![Health Check](https://img.shields.io/badge/health-passing-green.svg)

## 🚀 Quick Start

### For New Projects

1. **Clone and Initialize**:
   ```bash
   git clone <your-repo-url>
   cd your-project
   python template_source/scripts/init_project.py
   ```

2. **Configure LLM Provider**:
   ```bash
   ./squad --config-llm
   ```

3. **Start Coding**:
   ```bash
   ./squad --task "Build a REST API for user management"
   ```

### For Existing Projects

1. **Initialize in Integration Mode**:
   ```bash
   python template_source/scripts/init_project.py
   # Follow prompts to integrate with existing codebase
   ```

2. **Health Check**:
   ```bash
   python scripts/health_check.py
   ```

## 📋 Features

### 🤖 Multi-Agent Architecture
- **Brain**: Strategic planning and architecture
- **Boom**: Feature development and implementation
- **Sentinel**: Security, compliance, and code review
- **Bolt**: Code refactoring and optimization
- **Scribe**: Documentation and knowledge management
- **Additional Agents**: QA, Design, Release Management, and more

### 🛠️ Command Interface
Trigger specialized workflows with simple commands:
```bash
/standup "Design user authentication system"
/judge "Review this authentication code"
/test "Generate test cases for login"
/panic "Fix critical security vulnerability"
/audit "Analyze codebase health"
```

### 📊 System Management
- **Health Monitoring**: Real-time system diagnostics
- **Backup/Restore**: Safe configuration management
- **Auto-Updates**: Seamless system maintenance
- **Plugin System**: Extensible functionality

### 🔒 Security & Compliance
- Zero-trust architecture
- Automated security scanning
- Compliance validation
- Safe dependency management

## 📖 Documentation

- **[What's New](WHATS_NEW.md)** - Latest features and improvements
- **[Agent Commands](.agents/COMMANDS.md)** - Complete command reference
- **[System Architecture](.agents/README.md)** - Technical overview
- **[Utilities Guide](docs/UTILITIES.md)** - System management tools
- **[Solo Developer Guide](docs/SOLO_DEV_CODEX.md)** - Best practices
- **[Study Guide](docs/STUDY_GUIDE.md)** - Learning resources
- **[Changelog](CHANGELOG.md)** - Version history and updates

## 🏗️ Project Structure

```
├── .agents/                 # Agent system core
│   ├── engine/             # Main execution engine
│   ├── config/             # Agent personalities
│   ├── workflows/          # Specialized processes
│   ├── rules/              # Coding standards
│   ├── memory/             # Session logs & knowledge
│   └── plugins/            # Extensibility system
├── scripts/                # Utility scripts
│   ├── init_project.py     # System initialization
│   ├── health_check.py     # System diagnostics
│   ├── backup_restore.py   # Configuration backup
│   └── update.py           # System updates
├── src/                    # Your application code
├── tests/                  # Test suites
└── docs/                   # Documentation
```

## ⚙️ Configuration

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure LLM providers
./squad --config-llm
```

### System Management
```bash
# Check system health
python scripts/health_check.py

# Backup configuration
python scripts/backup_restore.py backup

# Check for updates
python scripts/update.py --check

# View system status
./squad --status
```

## 🔧 Advanced Usage

### Custom Workflows
Create specialized workflows in `.agents/workflows/`:
```markdown
# .agents/workflows/custom_workflow.md
## Custom Process
1. Analyze requirements
2. Generate implementation
3. Test thoroughly
4. Deploy safely
```

### Plugin Development
Extend functionality with plugins in `.agents/plugins/`:
```python
# .agents/plugins/my_plugin.py
PLUGIN_INFO = {
    'name': 'My Plugin',
    'version': '1.0.0',
    'description': 'Custom functionality',
    'author': 'Your Name'
}

def on_session_start(task):
    print(f"Custom plugin activated for: {task}")
```

If present, `.agents/plugins/allowed_plugins.json` controls which plugins are permitted to load, and may include SHA-256 hash entries for stronger integrity checks.

### Command Line Options
```bash
# Initialize with options
python scripts/init_project.py --dry-run    # Preview changes
python scripts/init_project.py --force      # Override safety checks

# Direct engine usage
./squad --task "Implement feature X"
./squad --file path/to/file.py
./squad --llm openai --model-path gpt-4
```

## 🔍 Troubleshooting

### Common Issues

**Initialization fails with dependency errors**:
```bash
# Install required packages
pip install PyYAML python-dotenv jsonschema
python scripts/init_project.py
```

**LLM configuration issues**:
```bash
# Reconfigure LLM providers
./squad --config-llm
```

**System health problems**:
```bash
# Run diagnostics
python scripts/health_check.py

# Restore from backup
python scripts/backup_restore.py restore --file backup.tar.gz

# Restore safety
The restore process validates archive contents to prevent path traversal and rejects symlinks or unsafe archive members.
```

### Getting Help
- Run `./squad --help` for command options
- Check `.agents/docs/USER_MANUAL.md` for detailed guides
- Use `/sidebar` in prompts for direct assistance

## 🤝 Contributing

This system is designed for extensibility. Contributions welcome:
- New agent workflows
- Plugin development
- Documentation improvements
- Bug fixes and enhancements

## 📄 License

Licensed under the [GNU Affero General Public License v3.0](/LICENSE).

---

**Built with ❤️ for the future of collaborative software development**
