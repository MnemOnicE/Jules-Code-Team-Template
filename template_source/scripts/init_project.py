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
    with open(filepath, 'r') as f:
        content = f.read()
    new_content = re.sub(search_pattern, replace_value, content, flags=re.MULTILINE)
    with open(filepath, 'w') as f:
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
            os.chmod(dst_path, 0o755)

    print("Brain: Installed Git safeguards (pre-commit, pre-push).")


def configure_git_remote(is_migration=False):

    print("\nBrain: Securing Git Endpoints (Non-Negotiable)")

    # Do not wipe the user's remote if this is an integration/migration!
    if is_migration:
        print("Brain: Integration mode detected. Skipping Git remote reconfiguration to protect existing repository.")
        return

    try:
        subprocess.run(["git", "remote", "remove", "origin"], stderr=subprocess.DEVNULL)
        print("✅ Removed template remote 'origin'.")
    except Exception:
        pass

    new_remote = input("Brain: Enter your new Git repository URL (HTTPS or SSH), or leave blank to skip for now: ").strip()
    if new_remote:
        try:
            subprocess.run(["git", "remote", "add", "origin", new_remote], check=True)
            print(f"✅ Added new remote 'origin': {new_remote}")
        except Exception as e:
            print(f"⚠️ Failed to add remote: {e}")

def main(dry_run=False, force=False):

    clear_screen()
    print_header()

    ROOT = os.getcwd()
    TEMPLATE_DIR = os.path.join(ROOT, "template_source")

    # --- [START PATCH] SNAPSHOT SAFETY CHECK ---
    # Stops the script from destroying the repo if re-run after initialization.
    if not os.path.exists(TEMPLATE_DIR):
        print("Brain: System already initialized. Skipping onboarding.")
        return
    # --- [END PATCH] ---------------------------

    if dry_run:
        print("🧪 DRY RUN MODE: Simulating initialization without making changes.")
        print("This will show what would happen without actually modifying files.\n")

    # 0. Environment Scan (Migration Detection)
    # We check for files that are NOT part of the template mechanism
    # Added src, tests, etc. to ignored list so fresh clones don't trigger Migration Mode
    ignored_items = {'.git', 'template_source', 'README.md', 'LICENSE', 'CONTRIBUTING.md', '.DS_Store', 'tests', 'requirements.txt', 'package.json', 'package-lock.json', '.agents'}
    existing_items = set(os.listdir(ROOT)) - ignored_items

    IS_MIGRATION = len(existing_items) > 0

    if IS_MIGRATION:
        print(f"Brain: ⚠️  Existing infrastructure detected ({len(existing_items)} items).")
        print("Brain: Switching to \033[1mINTEGRATION MODE\033[0m. I will join your team, not replace it.")
    else:
        print("Brain: ✨ Fresh field detected. Switching to \033[1mGENESIS MODE\033[0m.")

    print("\n---------------------------------------------")

    # 1. The Interview
    print("Brain: I am waking up. I need to understand the mission parameters.\n")
    print("💡 Tip: Press Enter to accept defaults in brackets []\n")

    if IS_MIGRATION:
        project_name = get_input("Brain: What is the name of this existing project?", os.path.basename(ROOT))
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
    print(f"   Mode: {'INTEGRATION' if IS_MIGRATION else 'GENESIS'}")

    confirm = get_input("\nBrain: Ready to proceed? (Y/n)", "Y")
    if confirm.lower() not in ['y', 'yes', '']:
        print("Brain: Initialization cancelled.")
        return

    if dry_run:
        print("🧪 Would configure squad parameters...")
        return  # Exit early for dry run

    AGENTS_DIR = os.path.join(TEMPLATE_DIR, ".agents")
    RULES_DIR = os.path.join(AGENTS_DIR, "rules")
    DOCS_DIR = os.path.join(AGENTS_DIR, "docs")
    CONFIG_DIR = os.path.join(AGENTS_DIR, "config")

    # 2. File Operations - Merge AGENTS.md (System Context)
    print("Brain: absorbing system context...")
    root_agents_md = os.path.join(ROOT, "AGENTS.md")
    workflow_rules_md = os.path.join(RULES_DIR, "WORKFLOW_RULES.md")

    if os.path.exists(root_agents_md) and os.path.exists(workflow_rules_md):
        with open(root_agents_md, 'r') as f:
            agents_content = f.read()
        with open(workflow_rules_md, 'r') as f:
            rules_content = f.read()

        # Prepend context to rules
        final_content = f"## 0. System Context & Ingestion\n{agents_content}\n\n{rules_content}"
        with open(workflow_rules_md, 'w') as f:
            f.write(final_content)
        os.remove(root_agents_md)

    # 3. Update Configurations (Personas)
    brain_config = os.path.join(CONFIG_DIR, "brain.md")
    update_file(brain_config, r"\*\*Current Mode:\*\* Democracy", f"**Current Mode:** {governance}")

    sentinel_config = os.path.join(CONFIG_DIR, "sentinel.md")
    update_file(sentinel_config, r"\*\*Role:\*\* Security & Compliance\.", f"**Role:** Security & Compliance.\n**Risk Tolerance:** {risk}")

    boom_config = os.path.join(CONFIG_DIR, "boom.md")
    update_file(boom_config, r"\*\*Role:\*\* Feature Delivery\.", f"**Role:** Feature Delivery.\n**Project Context:** {project_context}")

    # 4. Unpack Template (The Smart Part)
    print("Brain: Unpacking project structure...")

    for item in os.listdir(TEMPLATE_DIR):
        s = os.path.join(TEMPLATE_DIR, item)
        d = os.path.join(ROOT, item)

        # Handle README (The Manual)
        if item == "README.md":
            # In Migration Mode, we DON'T overwrite the root README.
            # We move the template README to .agents/docs/USER_MANUAL.md
            if IS_MIGRATION:
                manual_dest = os.path.join(ROOT, ".agents", "docs", "USER_MANUAL.md")
                # We need to wait until .agents is moved first, so we'll handle this after the loop or ensure dir exists
                # Actually, simpler: Move it to d (ROOT/README.md) ONLY IF Creation Mode.
                pass # Handled below
            else:
                # Creation Mode: Overwrite Root README
                if os.path.exists(d): os.remove(d)
                shutil.move(s, d)
            continue

        # Handle .gitignore (Append vs Overwrite)
        if item == ".gitignore" and os.path.exists(d) and IS_MIGRATION:
            print("Brain: Merging .gitignore...")
            with open(s, 'r') as fsrc: template_ignore = fsrc.read()
            with open(d, 'a') as fdst:
                fdst.write("\n\n# --- JULES CODING SQUAD ---\n")
                fdst.write(template_ignore)
            os.remove(s)
            continue

        # Handle Scripts Folder (Merge)
        if item == "scripts":
             if os.path.exists(d):
                 for subitem in os.listdir(s):
                     shutil.move(os.path.join(s, subitem), os.path.join(d, subitem))
                 os.rmdir(s)
             else:
                 shutil.move(s, d)
             continue

        # Default Move (Overwrite if exists in Creation Mode, Skip/Merge in Migration?)
        # For .agents/ folder, we always want to install it.

        # Deploy wrapper script to root
        if item == "squad":
            if os.path.exists(d): os.remove(d)
            shutil.move(s, d)
            os.chmod(d, 0o755)
            continue

        if item == ".agents":
            if os.path.exists(d): shutil.rmtree(d) # Re-install agents
            shutil.move(s, d)
            continue

        # For src/ or other scaffold files, SKIP in Migration Mode
        if IS_MIGRATION and item in ['src', 'tests', 'package.json', 'requirements.txt']:
            print(f"Brain: Skipping scaffolding file '{item}' (preserving existing).")
            if os.path.isdir(s): shutil.rmtree(s)
            else: os.remove(s)
            continue

        # Fallback for anything else
        if os.path.exists(d):
            if os.path.isdir(d): shutil.rmtree(d)
            else: os.remove(d)
        shutil.move(s, d)

    # Post-Loop Handling for Manual in Migration Mode
    if IS_MIGRATION:
        # The template README is still in TEMPLATE_DIR (we skipped it loop) or deleted?
        # Wait, if we skipped it, it's still in TEMPLATE_DIR.
        template_readme = os.path.join(TEMPLATE_DIR, "README.md")
        manual_dest_dir = os.path.join(ROOT, ".agents", "docs")
        manual_dest = os.path.join(manual_dest_dir, "USER_MANUAL.md")

        if os.path.exists(template_readme):
            if not os.path.exists(manual_dest_dir): os.makedirs(manual_dest_dir)
            shutil.move(template_readme, manual_dest)

            # Append Badge to Root README
            root_readme = os.path.join(ROOT, "README.md")
            if os.path.exists(root_readme):
                with open(root_readme, 'a') as f:
                    f.write("\n\n> 🧠 **This project is now managed by The Coding Squad.**\n> See `.agents/docs/USER_MANUAL.md` for commands.\n")

    # 5. The Lift (Runtime Sanitization)
    print("Brain: Lifting Runtime Engine...")

    # Define sanitization targets
    cleanup_targets = [
        os.path.join(ROOT, 'ingests'),
        os.path.join(ROOT, 'tests', 'verification', 'logs'),
        os.path.join(ROOT, 'tests', 'verification', '.hypothesis'),
        os.path.join(ROOT, '.hypothesis'),
        os.path.join(ROOT, '__pycache__'),
        os.path.join(ROOT, '__pycache__'),
        os.path.join(ROOT, 'core', '__pycache__')
    ]

    # Recursive cleaning for __pycache__
    for root, dirs, files in os.walk(ROOT):
        if '__pycache__' in dirs:
            shutil.rmtree(os.path.join(root, '__pycache__'))
            dirs.remove('__pycache__') # Stop descending
        if '.hypothesis' in dirs:
             shutil.rmtree(os.path.join(root, '.hypothesis'))
             dirs.remove('.hypothesis')

    # Specific targets
    for target in cleanup_targets:
        if os.path.exists(target):
            if os.path.isdir(target):
                shutil.rmtree(target)
            else:
                os.remove(target)

    # 6. Cleanup (Template Source)
    try:
        if os.path.exists(TEMPLATE_DIR): shutil.rmtree(TEMPLATE_DIR)
    except OSError as e:
        print(f"Warning: Failed to cleanup template source: {e}")

    # 7. Git Endpoint Security and Hooks
    configure_git_remote(IS_MIGRATION)
    install_git_hooks()

    # 7.5 LLM Configuration
    # Safe import from core to survive template deletion


    import sys
    sys.path.insert(0, os.path.join(ROOT, ".agents", "engine"))
    from core.llm_config import configure_llm_providers
    configure_llm_providers()

    # 8. Trigger Smart Ingest (The Awakening)
    print("Brain: Initializing memory systems...")
    ingest_script = os.path.join(ROOT, "scripts", "smart_ingest.py")
    if os.path.exists(ingest_script):
        try:
            # We run it with python executable
            subprocess.run([sys.executable, ingest_script], check=False)
        except Exception as e:
            print(f"⚠️ Warning: Could not auto-run ingestion: {e}")

    print("\n---------------------------------------------")
    print(f"✅ Brain: {project_name} initialized.")
    print(f"✅ Mode: {'INTEGRATION' if IS_MIGRATION else 'GENESIS'}")
    if IS_MIGRATION:
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
