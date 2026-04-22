#!/usr/bin/env python3

# Jules Code Team Template
# Copyright (C) 2026  MnemOnicE
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
🧠 CODING SQUAD ONBOARDING PROTOCOL
-----------------------------------
ARCHITECTURAL CONSTRAINT: ZERO-DEPENDENCY
This script runs BEFORE the environment is set up.
It must ONLY use Python standard libraries (os, sys, json, shutil, re, subprocess, pathlib).
DO NOT import third-party packages.
"""
import os
import shutil
import re
import sys
import json
import subprocess
import importlib.util
import argparse
import stat
from pathlib import Path

def check_dependencies():
    required_packages = {
        'yaml': 'PyYAML',
        'dotenv': 'python-dotenv',
        'gitingest': 'gitingest',
        'jsonschema': 'jsonschema'
    }
    missing = []
    for module_name, pip_name in required_packages.items():
        try:
            if importlib.util.find_spec(module_name) is None:
                missing.append(pip_name)
        except (ValueError, ImportError):
            missing.append(pip_name)

    if missing:
        print("\n\033[1;33m⚠️ Missing Required Dependencies detected.\033[0m")
        print("Attempting to auto-install the following packages:")
        for pkg in missing:
            print(f"  - {pkg}")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install"] + missing, check=True, shell=False)
            print("\033[1;32m✅ Dependencies installed successfully.\033[0m\n")
        except subprocess.CalledProcessError:
            print("\n\033[1;31m❌ CRITICAL: Failed to auto-install dependencies.\033[0m")
            print("Please ensure you have internet access and the correct permissions, or run:")
            print("\033[1;36m  python3 -m venv venv")
            print("  source venv/bin/activate  # Or venv\\Scripts\\activate on Windows")
            print("  pip install " + " ".join(missing) + "\033[0m\n")
            sys.exit(1)

def validate_governance(value):
    return value.lower() in ['democracy', 'dictator']

def validate_risk(value):
    return value.lower() in ['high', 'medium', 'low']

def validate_git_remote(url):
    """
    Validates the Git remote URL for security.
    Blocks option injection (starts with -) and dangerous protocols (ext::).
    """
    if not url:
        return True
    if url.strip().startswith("-"):
        return False
    if "ext::" in url.lower():
        return False
    return True

def _is_safe_path(path_str):
    """
    Prevents path traversal by ensuring the path doesn't contain parent directory references
    or absolute paths that point outside the intended root.
    """
    return ".." not in path_str and not os.path.isabs(path_str)

def clear_screen():
    print("\033[H\033[J", end="")

def print_header():
    print("🧠 \033[1mBrain: Initializing Onboarding Protocol...\033[0m")
    print("---------------------------------------------")
    print("Welcome to Jules Code Team Template!")
    print("This script will set up AI-powered coding assistants for your project.")
    print("Answer a few questions, and we'll get you started.\n")

def get_input(prompt, default=None, validator=None):
    while True:
        try:
            if default:
                user_input = input(f"{prompt} [{default}]: ")
                value = user_input if user_input.strip() else default
            else:
                value = input(f"{prompt}: ")
        except EOFError:
            return default
        
        if validator and not validator(value):
            print("❌ Invalid input. Please try again.")
            continue
        return value

def update_file(filepath, search_pattern, replace_value):
    path = Path(filepath)
    if not path.exists():
        return
    content = path.read_text(encoding='utf-8')
    new_content = re.sub(search_pattern, replace_value, content, flags=re.MULTILINE)
    path.write_text(new_content, encoding='utf-8')

def install_git_hooks():
    hooks_dir = Path.cwd() / '.git' / 'hooks'
    if not hooks_dir.exists():
        return

    template_hooks_dir = Path(__file__).resolve().parent / 'hooks_templates'
    if not template_hooks_dir.exists():
        return

    for hook_name in ['pre-commit', 'pre-push']:
        src_path = template_hooks_dir / hook_name
        dst_path = hooks_dir / hook_name
        if src_path.exists():
            shutil.copy2(src_path, dst_path)
            # Security: Use stat constants instead of octal
            dst_path.chmod(stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

    print("Brain: Installed Git safeguards (pre-commit, pre-push).")

def configure_git_remote(is_migration=False):
    print("\nBrain: Securing Git Endpoints (Non-Negotiable)")
    if is_migration:
        print("Brain: Integration mode detected. Skipping Git remote reconfiguration to protect existing repository.")
        return

    try:
        subprocess.run(["git", "remote", "remove", "origin"], stderr=subprocess.DEVNULL, check=False, shell=False)
        print("✅ Removed template remote 'origin'.")
    except Exception:
        pass

    new_remote = input("Brain: Enter your new Git repository URL (HTTPS or SSH), or leave blank to skip for now: ").strip()
    if new_remote:
        if not validate_git_remote(new_remote):
            print(f"❌ Security Error: Invalid or dangerous Git remote URL: {new_remote}")
            return

        try:
            # Security: Use -- to separate options from arguments
            subprocess.run(["git", "remote", "add", "origin", "--", new_remote], check=True, shell=False)
            print(f"✅ Added new remote 'origin': {new_remote}")
        except Exception as e:
            print(f"⚠️ Failed to add remote: {e}")

def scan_environment(root_path):
    ignored_items = {'.git', 'template_source', 'README.md', 'LICENSE', 'CONTRIBUTING.md', '.DS_Store', 'tests', 'requirements.txt', 'package.json', 'package-lock.json', '.agents'}
    existing_items = set(os.listdir(root_path)) - ignored_items
    return len(existing_items) > 0, existing_items

def conduct_interview(is_migration, root_path):
    print("\n---------------------------------------------")
    print("Brain: I am waking up. I need to understand the mission parameters.\n")
    print("💡 Tip: Press Enter to accept defaults in brackets []\n")

    if is_migration:
        project_name = get_input("Brain: What is the name of this existing project?", Path(root_path).name)
        project_context = get_input("Brain: Briefly describe what this code does (for my context)", "Legacy Codebase")
    else:
        project_name = get_input("Brain: First, what is the Project Name?", "MyNewProject")
        project_context = get_input("Brain: What are we building? (SaaS, Game, Library?)", "SaaS")

    print("\n🤖 Governance determines how decisions are made:")
    print("   Democracy: All agents vote on changes")
    print("   Dictator: Lead agent makes final decisions")
    governance = get_input("Brain: Governance Mode? (Democracy/Dictator)", "Democracy", validate_governance)
    
    print("\n⚠️  Risk tolerance affects security and speed:")
    print("   High: Fast but less secure")
    print("   Medium: Balanced approach")
    print("   Low: Secure but slower")
    risk = get_input("Brain: Risk Tolerance? (High/Medium/Low)", "Low", validate_risk)

    print("\nBrain: Configuring squad parameters...")
    print("\n📋 Configuration Summary:")
    print(f"   Project: {project_name}")
    print(f"   Context: {project_context}")
    print(f"   Governance: {governance}")
    print(f"   Risk Level: {risk}")
    print(f"   Mode: {'INTEGRATION' if is_migration else 'GENESIS'}")

    confirm = get_input("\nBrain: Ready to proceed? (Y/n)", "Y")
    if confirm.lower() not in ['y', 'yes', '']:
        print("Brain: Initialization cancelled.")
        return None

    return {
        'name': project_name,
        'context': project_context,
        'governance': governance,
        'risk': risk
    }

def unpack_template(root_path, template_dir, params, is_migration):
    print("Brain: Unpacking project structure...")
    root = Path(root_path)
    template = Path(template_dir)
    agents_dir = template / ".agents"
    config_dir = agents_dir / "config"
    rules_dir = agents_dir / "rules"

    # 1. Merge AGENTS.md
    print("Brain: absorbing system context...")
    root_agents_md = root / "AGENTS.md"
    workflow_rules_md = rules_dir / "WORKFLOW_RULES.md"

    if root_agents_md.exists() and workflow_rules_md.exists():
        agents_content = root_agents_md.read_text(encoding='utf-8')
        rules_content = workflow_rules_md.read_text(encoding='utf-8')
        final_content = f"## 0. System Context & Ingestion\n{agents_content}\n\n{rules_content}"
        workflow_rules_md.write_text(final_content, encoding='utf-8')
        root_agents_md.unlink()

    # 2. Update Configurations
    update_file(config_dir / "brain.md", r"\*\*Current Mode:\*\* Democracy", f"**Current Mode:** {params['governance']}")
    update_file(config_dir / "sentinel.md", r"\*\*Role:\*\* Security & Compliance\.", f"**Role:** Security & Compliance.\n**Risk Tolerance:** {params['risk']}")
    update_file(config_dir / "boom.md", r"\*\*Role:\*\* Feature Delivery\.", f"**Role:** Feature Delivery.\n**Project Context:** {params['context']}")

    # 3. Move items
    for item in os.listdir(template):
        if not _is_safe_path(item): continue
        s = template / item
        d = root / item

        if item == "README.md":
            if is_migration:
                # Handled later
                continue
            if d.exists(): d.unlink()
            shutil.move(str(s), str(d))
            continue

        if item == ".gitignore" and d.exists() and is_migration:
            print("Brain: Merging .gitignore...")
            template_ignore = s.read_text(encoding='utf-8')
            with d.open('a', encoding='utf-8') as f:
                f.write("\n\n# --- JULES CODING SQUAD ---\n")
                f.write(template_ignore)
            s.unlink()
            continue

        if item == "scripts":
             if d.exists():
                 for subitem in os.listdir(s):
                     if not _is_safe_path(subitem): continue
                     shutil.move(str(s / subitem), str(d / subitem))
                 shutil.rmtree(s)
             else:
                 shutil.move(str(s), str(d))
             continue

        if item == "squad":
            if d.exists(): d.unlink()
            shutil.move(str(s), str(d))
            d.chmod(stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
            continue

        if item == ".agents":
            if d.exists(): shutil.rmtree(d)
            shutil.move(str(s), str(d))
            continue

        if is_migration and item in ['src', 'tests', 'package.json', 'requirements.txt']:
            print(f"Brain: Skipping scaffolding file '{item}' (preserving existing).")
            if s.is_dir(): shutil.rmtree(s)
            else: s.unlink()
            continue

        if d.exists():
            if d.is_dir(): shutil.rmtree(d)
            else: d.unlink()
        shutil.move(str(s), str(d))

    if is_migration:
        template_readme = template / "README.md"
        manual_dest_dir = root / ".agents" / "docs"
        manual_dest = manual_dest_dir / "USER_MANUAL.md"

        if template_readme.exists():
            manual_dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(template_readme), str(manual_dest))
            root_readme = root / "README.md"
            if root_readme.exists():
                with root_readme.open('a', encoding='utf-8') as f:
                    f.write("\n\n> 🧠 **This project is now managed by The Coding Squad.**\n> See `.agents/docs/USER_MANUAL.md` for commands.\n")

def sanitize_runtime(root_path):
    print("Brain: Lifting Runtime Engine...")
    root = Path(root_path)
    cleanup_targets = [
        root / 'ingests',
        root / 'tests' / 'verification' / 'logs',
        root / 'tests' / 'verification' / '.hypothesis',
        root / '.hypothesis',
        root / '__pycache__',
        root / 'core' / '__pycache__'
    ]

    for r, dirs, _ in os.walk(root):
        curr_root = Path(r)
        for d in list(dirs):
            if d in ('__pycache__', '.hypothesis'):
                target = curr_root / d
                if target.resolve().is_relative_to(root.resolve()):
                    shutil.rmtree(target)
                dirs.remove(d)

    for target in cleanup_targets:
        if target.exists():
            if target.resolve().is_relative_to(root.resolve()):
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()

def finalize_initialization(root_path, params, is_migration):
    root = Path(root_path)
    configure_git_remote(is_migration)
    install_git_hooks()

    # LLM Configuration
    sys.path.insert(0, str(root / ".agents" / "engine"))
    try:
        from core.llm_config import configure_llm_providers
        configure_llm_providers()
    except (ImportError, Exception) as e:
        print(f"⚠️ Warning: Could not auto-configure LLM: {e}")

    # Trigger Smart Ingest
    print("Brain: Initializing memory systems...")
    ingest_script = root / "scripts" / "smart_ingest.py"
    if ingest_script.exists():
        try:
            spec = importlib.util.spec_from_file_location("smart_ingest", ingest_script)
            if spec and spec.loader:
                smart_ingest = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(smart_ingest)
                if hasattr(smart_ingest, 'main'):
                    smart_ingest.main()
        except Exception as e:
            print(f"⚠️ Warning: Could not auto-run ingestion: {e}")

    print("\n---------------------------------------------")
    print(f"✅ Brain: {params['name']} initialized.")
    print(f"✅ Mode: {'INTEGRATION' if is_migration else 'GENESIS'}")
    if is_migration:
        print(f"ℹ️  Manual installed at: .agents/docs/USER_MANUAL.md")
    else:
        print(f"ℹ️  See README.md for instructions.")
    
    print("\n🚀 Next Steps:")
    print("   1. Run './squad' to start the coding assistant")
    print("   2. Try '/standup' to begin your first session")
    print("   3. Check .agents/config/ for agent configurations")
    print("\n🆘 Need help? Run './squad --help' or check the documentation.")

def main(dry_run=False, force=False):
    clear_screen()
    print_header()

    ROOT = os.getcwd()
    TEMPLATE_DIR = os.path.join(ROOT, "template_source")

    if not Path(TEMPLATE_DIR).exists() and not force:
        print("Brain: System already initialized. Skipping onboarding.")
        return

    if dry_run:
        print("🧪 DRY RUN MODE: Simulating initialization without making changes.\n")

    is_migration, _ = scan_environment(ROOT)
    if is_migration:
        print("Brain: Existing infrastructure detected. Switching to \033[1mINTEGRATION MODE\033[0m.")
    else:
        print("Brain: ✨ Fresh field detected. Switching to \033[1mGENESIS MODE\033[0m.")

    params = conduct_interview(is_migration, ROOT)
    if not params:
        return

    if dry_run:
        print("🧪 Would configure squad parameters and unpack template...")
        return

    unpack_template(ROOT, TEMPLATE_DIR, params, is_migration)
    sanitize_runtime(ROOT)

    try:
        if Path(TEMPLATE_DIR).exists():
            shutil.rmtree(TEMPLATE_DIR)
    except OSError as e:
        print(f"Warning: Failed to cleanup template source: {e}")

    finalize_initialization(ROOT, params, is_migration)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🧠 Jules Code Team Template Initialization Script")
    parser.add_argument('--dry-run', action='store_true', help='Simulate initialization')
    parser.add_argument('--force', action='store_true', help='Force initialization')
    args = parser.parse_args()

    check_dependencies()
    main(dry_run=args.dry_run, force=args.force)
