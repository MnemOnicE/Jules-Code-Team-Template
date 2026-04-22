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
It must ONLY use Python standard libraries (os, sys, json, shutil, re, subprocess).
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
            subprocess.run([sys.executable, "-m", "pip", "install", "--"] + missing, check=True, shell=False)
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
    Blocks option injection (starts with -) and dangerous protocols.
    """
    if not url:
        return True
    url = url.strip()
    # Prevent option injection
    if url.startswith("-"):
        return False

    # Block dangerous protocols
    blacklist = ['ext::', 'git-remote-']
    url_lower = url.lower()
    for pattern in blacklist:
        if pattern in url_lower:
            return False

    # Basic scheme validation if it looks like a URL
    if "://" in url:
        scheme = url.split("://")[0].lower()
        if scheme not in ['https', 'http', 'git', 'ssh']:
            return False

    return True

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
        if default:
            user_input = input(f"{prompt} [{default}]: ")
            value = user_input if user_input.strip() else default
        else:
            value = input(f"{prompt}: ")
        
        if validator and not validator(value):
            print("❌ Invalid input. Please try again.")
            continue
        return value

def update_file(filepath, search_pattern, replace_value):
    path = Path(filepath)
    if not path.exists():
        return
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    new_content = re.sub(search_pattern, replace_value, content, flags=re.MULTILINE)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)

def install_git_hooks():
    root = Path.cwd()
    hooks_dir = root / '.git' / 'hooks'
    if not hooks_dir.is_dir():
        return

    template_hooks_dir = Path(__file__).resolve().parent / 'hooks_templates'
    if not template_hooks_dir.is_dir():
        return

    for hook_name in ['pre-commit', 'pre-push']:
        src_path = template_hooks_dir / hook_name
        dst_path = hooks_dir / hook_name
        if src_path.exists():
            shutil.copy2(src_path, dst_path)
            dst_path.chmod(stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

    print("Brain: Installed Git safeguards (pre-commit, pre-push).")

def configure_git_remote(is_migration=False):
    print("\nBrain: Securing Git Endpoints (Non-Negotiable)")

    if is_migration:
        print("Brain: Integration mode detected. Skipping Git remote reconfiguration to protect existing repository.")
        return

    try:
        subprocess.run(["git", "remote", "remove", "origin"], stderr=subprocess.DEVNULL, shell=False)
        print("✅ Removed template remote 'origin'.")
    except Exception:
        pass

    new_remote = input("Brain: Enter your new Git repository URL (HTTPS or SSH), or leave blank to skip for now: ").strip()
    if new_remote:
        if not validate_git_remote(new_remote):
            print(f"❌ Security Error: Invalid or dangerous Git remote URL: {new_remote}")
            return

        try:
            subprocess.run(["git", "remote", "add", "origin", "--", new_remote], check=True, shell=False)
            print(f"✅ Added new remote 'origin': {new_remote}")
        except Exception as e:
            print(f"⚠️ Failed to add remote: {e}")

def _is_safe_path(path_str):
    """Basic path traversal prevention."""
    return not (".." in path_str or path_str.startswith("/") or path_str.startswith("~"))

def main(dry_run=False, force=False):
    clear_screen()
    print_header()

    root = Path.cwd()
    template_dir = root / "template_source"

    if not template_dir.exists() and not force:
        print("Brain: System already initialized. Skipping onboarding. Use --force to re-initialize.")
        return

    if dry_run:
        print("🧪 DRY RUN MODE: Simulating initialization without making changes.")
        print("This will show what would happen without actually modifying files.\n")

    ignored_items = {'.git', 'template_source', 'README.md', 'LICENSE', 'CONTRIBUTING.md', '.DS_Store', 'tests', 'requirements.txt', 'package.json', 'package-lock.json', '.agents'}
    existing_items = set(os.listdir(root)) - ignored_items

    is_migration = len(existing_items) > 0

    if is_migration:
        print(f"Brain: ⚠️  Existing infrastructure detected ({len(existing_items)} items).")
        print("Brain: Switching to \033[1mINTEGRATION MODE\033[0m. I will join your team, not replace it.")
    else:
        print("Brain: ✨ Fresh field detected. Switching to \033[1mGENESIS MODE\033[0m.")

    print("\n---------------------------------------------")

    print("Brain: I am waking up. I need to understand the mission parameters.\n")
    print("💡 Tip: Press Enter to accept defaults in brackets []\n")

    if is_migration:
        project_name = get_input("Brain: What is the name of this existing project?", root.name)
        project_context = get_input("Brain: Briefly describe what this code does (for my context)", "Legacy Codebase")
    else:
        project_name = get_input("Brain: First, what is the Project Name?", "MyNewProject")
        project_context = get_input("Brain: What are we building? (SaaS, Game, Library?)", "SaaS")

    print("\n🤖 Governance determines how decisions are made:")
    governance = get_input("Brain: Governance Mode? (Democracy/Dictator)", "Democracy", validate_governance)
    
    print("\n⚠️  Risk tolerance affects security and speed:")
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
        return

    if dry_run:
        print("🧪 Would configure squad parameters...")
        return

    agents_dir = template_dir / ".agents"
    rules_dir = agents_dir / "rules"
    docs_dir = agents_dir / "docs"
    config_dir = agents_dir / "config"

    print("Brain: absorbing system context...")
    root_agents_md = root / "AGENTS.md"
    workflow_rules_md = rules_dir / "WORKFLOW_RULES.md"

    if root_agents_md.exists() and workflow_rules_md.exists():
        with open(root_agents_md, 'r', encoding='utf-8') as f:
            agents_content = f.read()
        with open(workflow_rules_md, 'r', encoding='utf-8') as f:
            rules_content = f.read()

        final_content = f"## 0. System Context & Ingestion\n{agents_content}\n\n{rules_content}"
        with open(workflow_rules_md, 'w', encoding='utf-8') as f:
            f.write(final_content)
        root_agents_md.unlink()

    brain_config = config_dir / "brain.md"
    update_file(brain_config, r"\*\*Current Mode:\*\* Democracy", f"**Current Mode:** {governance}")

    sentinel_config = config_dir / "sentinel.md"
    update_file(sentinel_config, r"\*\*Role:\*\* Security & Compliance\.", f"**Role:** Security & Compliance.\n**Risk Tolerance:** {risk}")

    boom_config = config_dir / "boom.md"
    update_file(boom_config, r"\*\*Role:\*\* Feature Delivery\.", f"**Role:** Feature Delivery.\n**Project Context:** {project_context}")

    print("Brain: Unpacking project structure...")

    for item in os.listdir(template_dir):
        if not _is_safe_path(item): continue
        s = template_dir / item
        d = root / item

        if item == "README.md":
            if not is_migration:
                if d.exists(): d.unlink()
                shutil.move(str(s), str(d))
            continue

        if item == ".gitignore" and d.exists() and is_migration:
            print("Brain: Merging .gitignore...")
            with open(s, 'r', encoding='utf-8') as fsrc: template_ignore = fsrc.read()
            with open(d, 'a', encoding='utf-8') as fdst:
                fdst.write("\n\n# --- JULES CODING SQUAD ---\n")
                fdst.write(template_ignore)
            s.unlink()
            continue

        if item == "scripts":
             if d.is_dir():
                 for subitem in os.listdir(s):
                     if _is_safe_path(subitem):
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
            if d.is_dir(): shutil.rmtree(d)
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
        template_readme = template_dir / "README.md"
        manual_dest_dir = root / ".agents" / "docs"
        manual_dest = manual_dest_dir / "USER_MANUAL.md"

        if template_readme.exists():
            if not manual_dest_dir.is_dir(): manual_dest_dir.mkdir(parents=True)
            shutil.move(str(template_readme), str(manual_dest))

            root_readme = root / "README.md"
            if root_readme.exists():
                with open(root_readme, 'a', encoding='utf-8') as f:
                    f.write("\n\n> 🧠 **This project is now managed by The Coding Squad.**\n> See `.agents/docs/USER_MANUAL.md` for commands.\n")

    print("Brain: Lifting Runtime Engine...")

    cleanup_targets = [
        root / 'ingests',
        root / 'tests' / 'verification' / 'logs',
        root / 'tests' / 'verification' / '.hypothesis',
        root / '.hypothesis',
        root / '__pycache__',
        root / 'core' / '__pycache__'
    ]

    for r, dirs, files in os.walk(root):
        if '__pycache__' in dirs:
            shutil.rmtree(Path(r) / '__pycache__')
            dirs.remove('__pycache__')
        if '.hypothesis' in dirs:
             shutil.rmtree(Path(r) / '.hypothesis')
             dirs.remove('.hypothesis')

    for target in cleanup_targets:
        if target.exists():
            if target.is_dir(): shutil.rmtree(target)
            else: target.unlink()

    try:
        if template_dir.is_dir(): shutil.rmtree(template_dir)
    except OSError as e:
        print(f"Warning: Failed to cleanup template source: {e}")

    configure_git_remote(is_migration)
    install_git_hooks()

    sys.path.insert(0, str(root / ".agents" / "engine"))
    from core.llm_config import configure_llm_providers
    configure_llm_providers()

    print("Brain: Initializing memory systems...")
    ingest_script = root / "scripts" / "smart_ingest.py"
    if ingest_script.exists():
        try:
            subprocess.run([sys.executable, str(ingest_script)], check=False, shell=False)
        except Exception as e:
            print(f"⚠️ Warning: Could not auto-run ingestion: {e}")

    print("\n---------------------------------------------")
    print(f"✅ Brain: {project_name} initialized.")
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="🧠 Jules Code Team Template Initialization Script",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--force', action='store_true')

    args = parser.parse_args()
    check_dependencies()
    main(dry_run=args.dry_run, force=args.force)
