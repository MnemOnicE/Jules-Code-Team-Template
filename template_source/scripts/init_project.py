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
import stat
import importlib.util
import argparse

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
            subprocess.run([sys.executable, "-m", "pip", "install"] + missing, check=True)
            print("\033[1;32m✅ Dependencies installed successfully.\033[0m\n")
        except subprocess.CalledProcessError as e:
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
    if not os.path.exists(filepath):
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    new_content = re.sub(search_pattern, replace_value, content, flags=re.MULTILINE)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)


def install_git_hooks():
    hooks_dir = os.path.join(os.getcwd(), '.git', 'hooks')
    if not os.path.exists(hooks_dir):
        return

    template_hooks_dir = os.path.join(os.path.dirname(__file__), 'hooks_templates')
    if not os.path.exists(template_hooks_dir):
        # Fallback for when templates aren't available yet or are missing
        return

    for hook_name in ['pre-commit', 'pre-push']:
        src_path = os.path.join(template_hooks_dir, hook_name)
        dst_path = os.path.join(hooks_dir, hook_name)
        if os.path.exists(src_path):
            shutil.copy2(src_path, dst_path)
            # Use fixed permissions: 755 (Owner: rwx, Group: r-x, Others: r-x)
            os.chmod(dst_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

    print("Brain: Installed Git safeguards (pre-commit, pre-push).")


def configure_git_remote(is_migration=False):

    print("\nBrain: Securing Git Endpoints (Non-Negotiable)")

    # Do not wipe the user's remote if this is an integration/migration!
    if is_migration:
        print("Brain: Integration mode detected. Skipping Git remote reconfiguration to protect existing repository.")
        return

    try:
        subprocess.run(["git", "remote", "remove", "origin"], stderr=subprocess.DEVNULL, check=False)
        print("✅ Removed template remote 'origin'.")
    except (subprocess.SubprocessError, OSError):
        pass

    new_remote = input("Brain: Enter your new Git repository URL (HTTPS or SSH), or leave blank to skip for now: ").strip()
    if new_remote:
        if not validate_git_remote(new_remote):
            print(f"❌ Security Error: Invalid or dangerous Git remote URL: {new_remote}")
            return

        try:
            subprocess.run(["git", "remote", "add", "--", "origin", new_remote], check=True)
            print(f"✅ Added new remote 'origin': {new_remote}")
        except (subprocess.SubprocessError, OSError) as e:
            print(f"⚠️ Failed to add remote: {e}")

def scan_environment(root):
    """Detects if this is a fresh clone (Genesis) or an existing project (Integration)."""
    ignored_items = {'.git', 'template_source', 'README.md', 'LICENSE', 'CONTRIBUTING.md', '.DS_Store', 'tests', 'requirements.txt', 'package.json', 'package-lock.json', '.agents'}
    existing_items = set(os.listdir(root)) - ignored_items
    is_migration = len(existing_items) > 0

    if is_migration:
        print(f"Brain: ⚠️  Existing infrastructure detected ({len(existing_items)} items).")
        print("Brain: Switching to \033[1mINTEGRATION MODE\033[0m. I will join your team, not replace it.")
    else:
        print("Brain: ✨ Fresh field detected. Switching to \033[1mGENESIS MODE\033[0m.")
    return is_migration

def run_interview(root, is_migration):
    """Gathers project parameters from the user."""
    print("Brain: I am waking up. I need to understand the mission parameters.\n")
    print("💡 Tip: Press Enter to accept defaults in brackets []\n")

    if is_migration:
        project_name = get_input("Brain: What is the name of this existing project?", os.path.basename(root))
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
        sys.exit(0)

    return project_name, project_context, governance, risk

def absorb_system_context(root, rules_dir):
    """Merges AGENTS.md into the workflow rules."""
    print("Brain: absorbing system context...")
    root_agents_md = os.path.join(root, "AGENTS.md")
    workflow_rules_md = os.path.join(rules_dir, "WORKFLOW_RULES.md")

    if os.path.exists(root_agents_md) and os.path.exists(workflow_rules_md):
        with open(root_agents_md, 'r', encoding='utf-8') as f:
            agents_content = f.read()
        with open(workflow_rules_md, 'r', encoding='utf-8') as f:
            rules_content = f.read()

        final_content = f"## 0. System Context & Ingestion\n{agents_content}\n\n{rules_content}"
        with open(workflow_rules_md, 'w', encoding='utf-8') as f:
            f.write(final_content)
        os.remove(root_agents_md)

def unpack_template(root, template_dir, is_migration):
    """Moves files from template_source to the project root."""
    print("Brain: Unpacking project structure...")
    for item in os.listdir(template_dir):
        s = os.path.join(template_dir, item)
        d = os.path.join(root, item)

        if item == "README.md":
            if not is_migration:
                if os.path.exists(d): os.remove(d)
                shutil.move(s, d)
            continue

        if item == ".gitignore" and os.path.exists(d) and is_migration:
            print("Brain: Merging .gitignore...")
            with open(s, 'r', encoding='utf-8') as fsrc: template_ignore = fsrc.read()
            with open(d, 'a', encoding='utf-8') as fdst:
                fdst.write("\n\n# --- JULES CODING SQUAD ---\n")
                fdst.write(template_ignore)
            os.remove(s)
            continue

        if item == "scripts":
             if os.path.exists(d):
                 for subitem in os.listdir(s):
                     shutil.move(os.path.join(s, subitem), os.path.join(d, subitem))
                 os.rmdir(s)
             else:
                 shutil.move(s, d)
             continue

        if item == "squad":
            if os.path.exists(d): os.remove(d)
            shutil.move(s, d)
            # Use fixed permissions: 755 (Owner: rwx, Group: r-x, Others: r-x)
            os.chmod(d, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
            continue

        if item == ".agents":
            if os.path.exists(d): shutil.rmtree(d)
            shutil.move(s, d)
            continue

        if is_migration and item in ['src', 'tests', 'package.json', 'requirements.txt']:
            print(f"Brain: Skipping scaffolding file '{item}' (preserving existing).")
            if os.path.isdir(s): shutil.rmtree(s)
            else: os.remove(s)
            continue

        if os.path.exists(d):
            if os.path.isdir(d): shutil.rmtree(d)
            else: os.remove(d)
        shutil.move(s, d)

def handle_migration_manual(root, template_dir):
    """Places the template README as USER_MANUAL.md in Integration Mode."""
    template_readme = os.path.join(template_dir, "README.md")
    manual_dest_dir = os.path.join(root, ".agents", "docs")
    manual_dest = os.path.join(manual_dest_dir, "USER_MANUAL.md")

    if os.path.exists(template_readme):
        if not os.path.exists(manual_dest_dir): os.makedirs(manual_dest_dir)
        shutil.move(template_readme, manual_dest)

        root_readme = os.path.join(root, "README.md")
        if os.path.exists(root_readme):
            with open(root_readme, 'a', encoding='utf-8') as f:
                f.write("\n\n> 🧠 **This project is now managed by The Coding Squad.**\n> See `.agents/docs/USER_MANUAL.md` for commands.\n")

def runtime_sanitization(root):
    """Cleans up temporary and cache files."""
    print("Brain: Lifting Runtime Engine...")
    cleanup_targets = [
        os.path.join(root, 'ingests'),
        os.path.join(root, 'tests', 'verification', 'logs'),
        os.path.join(root, 'tests', 'verification', '.hypothesis'),
        os.path.join(root, '.hypothesis'),
        os.path.join(root, '__pycache__'),
        os.path.join(root, 'core', '__pycache__')
    ]

    for current_root, dirs, _ in os.walk(root):
        for d in list(dirs):
            if d in ['__pycache__', '.hypothesis']:
                shutil.rmtree(os.path.join(current_root, d))
                dirs.remove(d)

    for target in cleanup_targets:
        if os.path.exists(target):
            if os.path.isdir(target): shutil.rmtree(target)
            else: os.remove(target)

def main(dry_run=False, force=False):
    clear_screen()
    print_header()

    ROOT = os.getcwd()
    TEMPLATE_DIR = os.path.join(ROOT, "template_source")

    if not os.path.exists(TEMPLATE_DIR):
        print("Brain: System already initialized. Skipping onboarding.")
        return

    if dry_run:
        print("🧪 DRY RUN MODE: Simulating initialization without making changes.\n")

    is_migration = scan_environment(ROOT)
    print("\n---------------------------------------------")

    project_name, project_context, governance, risk = run_interview(ROOT, is_migration)

    if dry_run:
        print("🧪 Would configure squad parameters...")
        return

    AGENTS_DIR = os.path.join(TEMPLATE_DIR, ".agents")
    absorb_system_context(ROOT, os.path.join(AGENTS_DIR, "rules"))

    # Update configurations
    config_dir = os.path.join(AGENTS_DIR, "config")
    update_file(os.path.join(config_dir, "brain.md"), r"\*\*Current Mode:\*\* Democracy", f"**Current Mode:** {governance}")
    update_file(os.path.join(config_dir, "sentinel.md"), r"\*\*Role:\*\* Security & Compliance\.", f"**Role:** Security & Compliance.\n**Risk Tolerance:** {risk}")
    update_file(os.path.join(config_dir, "boom.md"), r"\*\*Role:\*\* Feature Delivery\.", f"**Role:** Feature Delivery.\n**Project Context:** {project_context}")

    unpack_template(ROOT, TEMPLATE_DIR, is_migration)

    if is_migration:
        handle_migration_manual(ROOT, TEMPLATE_DIR)

    runtime_sanitization(ROOT)

    try:
        if os.path.exists(TEMPLATE_DIR): shutil.rmtree(TEMPLATE_DIR)
    except OSError as e:
        print(f"Warning: Failed to cleanup template source: {e}")

    configure_git_remote(is_migration)
    install_git_hooks()

    sys.path.insert(0, os.path.join(ROOT, ".agents", "engine"))
    from core.llm_config import configure_llm_providers
    configure_llm_providers()

    print("Brain: Initializing memory systems...")
    ingest_script = os.path.join(ROOT, "scripts", "smart_ingest.py")
    if os.path.exists(ingest_script):
        try:
            subprocess.run([sys.executable, ingest_script], check=False)
        except (subprocess.SubprocessError, OSError) as e:
            print(f"⚠️ Warning: Could not auto-run ingestion: {e}")

    print("\n---------------------------------------------")
    print(f"✅ Brain: {project_name} initialized.")
    print(f"✅ Mode: {'INTEGRATION' if is_migration else 'GENESIS'}")
    print(f"ℹ️  {'Manual installed at: .agents/docs/USER_MANUAL.md' if is_migration else 'See README.md for instructions.'}")
    print("\n🚀 Next Steps:")
    print("   1. Run './squad' to start the coding assistant")
    print("   2. Try '/standup' to begin your first session")
    print("\n🆘 Need help? Run './squad --help' or check the documentation.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="🧠 Jules Code Team Template Initialization Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python init_project.py                    # Interactive initialization
  python init_project.py --dry-run         # Preview what would happen
  python init_project.py --help            # Show this help

Modes:
  GENESIS: For new projects - creates full project structure
  INTEGRATION: For existing projects - integrates agents without overwriting

The script will automatically detect the appropriate mode based on existing files.
        """
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate initialization without making changes'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force initialization even if already initialized'
    )

    args = parser.parse_args()

    check_dependencies()
    main(dry_run=args.dry_run, force=args.force)
