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

def clear_screen():
    print("\033[H\033[J", end="")

def print_header():
    print("🧠 \033[1mBrain: Initializing Onboarding Protocol...\033[0m")
    print("---------------------------------------------")

def get_input(prompt, default=None):
    if default:
        user_input = input(f"{prompt} [{default}]: ")
        return user_input if user_input.strip() else default
    return input(f"{prompt}: ")

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

    # Create pre-commit hook
    pre_commit_path = os.path.join(hooks_dir, 'pre-commit')
    with open(pre_commit_path, 'w') as f:
        f.write('#!/bin/sh\n')
        f.write('echo "🛡️ Sentinel Check: Pre-commit hook executing"\n')
        f.write('exit 0\n')
    os.chmod(pre_commit_path, 0o755)

    # Create pre-push hook for endpoint validation
    pre_push_path = os.path.join(hooks_dir, 'pre-push')
    with open(pre_push_path, 'w') as f:
        f.write('#!/bin/sh\n')
        f.write('remote="$1"\n')
        f.write('url="$2"\n')
        f.write('echo "🛡️ Sentinel Check: Verifying push to $url"\n')
        f.write('if echo "$url" | grep -qi "template"; then\n')
        f.write('  echo "🚨 ERROR: Push to a repository containing \'template\' in the URL is blocked!"\n')
        f.write('  exit 1\n')
        f.write('fi\n')
        f.write('exit 0\n')
    os.chmod(pre_push_path, 0o755)
    print("Brain: Installed Git safeguards (pre-commit, pre-push).")


def configure_git_remote():

    print("\nBrain: Securing Git Endpoints (Non-Negotiable)")
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

def main():

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

    # 0. Environment Scan (Migration Detection)
    # We check for files that are NOT part of the template mechanism
    # Added src, tests, etc. to ignored list so fresh clones don't trigger Migration Mode
    ignored_items = {'.git', 'template_source', 'README.md', 'LICENSE', 'CONTRIBUTING.md', '.DS_Store', 'src', 'tests', 'requirements.txt', 'package.json', 'package-lock.json', '.agents'}
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

    if IS_MIGRATION:
        project_name = get_input("Brain: What is the name of this existing project?", os.path.basename(ROOT))
        project_context = get_input("Brain: Briefly describe what this code does (for my context)", "Legacy Codebase")
    else:
        project_name = get_input("Brain: First, what is the Project Name?", "MyNewProject")
        project_context = get_input("Brain: What are we building? (SaaS, Game, Library?)", "SaaS")

    governance = get_input("Brain: Governance Mode? (Democracy/Dictator)", "Democracy")
    risk = get_input("Brain: Risk Tolerance? (High/Medium/Low)", "Low")

    print("\nBrain: Configuring squad parameters...")

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
        os.path.join(ROOT, 'src', '__pycache__'),
        os.path.join(ROOT, 'src', 'core', '__pycache__')
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
    configure_git_remote()
    install_git_hooks()

    # 7.5 LLM Configuration
    # Safe import from core to survive template deletion
    from src.core.llm_config import configure_llm_providers
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
    print("\nRun '/standup' to begin.")

if __name__ == "__main__":
    main()
