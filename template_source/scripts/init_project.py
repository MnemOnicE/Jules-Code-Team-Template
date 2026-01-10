#!/usr/bin/env python3
"""
🧠 CODING SQUAD ONBOARDING PROTOCOL
-----------------------------------
ARCHITECTURAL CONSTRAINT: ZERO-DEPENDENCY
This script runs BEFORE the environment is set up.
It must ONLY use Python standard libraries (os, sys, json, shutil, re).
DO NOT import third-party packages (like requests, rich, or yaml).
"""
import os
import shutil
import re
import sys
import json

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
        print(f"⚠️ Warning: {filepath} not found.")
        return

    with open(filepath, 'r') as f:
        content = f.read()

    new_content = re.sub(search_pattern, replace_value, content, flags=re.MULTILINE)

    with open(filepath, 'w') as f:
        f.write(new_content)

def append_to_file(filepath, content_to_append):
    if not os.path.exists(filepath):
        return
    with open(filepath, 'a') as f:
        f.write("\n" + content_to_append)

def main():
    clear_screen()
    print_header()

    # 1. The Interview
    print("Brain: I am waking up. I need to understand the mission parameters.\n")

    project_name = get_input("Brain: First, what is the Project Name? (e.g., MySuperApp)", "MyNewProject")
    project_type = get_input("Brain: What are we building? (SaaS, Game, Library, Script?)", "SaaS")
    governance = get_input("Brain: Governance Mode? (Democracy/Dictator)", "Democracy")
    risk = get_input("Brain: Risk Tolerance? (High/Medium/Low)", "Low")

    print("\nBrain: Configuring squad parameters...")

    # Paths (relative to root where script is run)
    ROOT = os.getcwd()
    TEMPLATE_DIR = os.path.join(ROOT, "template_source")
    AGENTS_DIR = os.path.join(TEMPLATE_DIR, ".agents")
    RULES_DIR = os.path.join(AGENTS_DIR, "rules")
    DOCS_DIR = os.path.join(AGENTS_DIR, "docs")
    CONFIG_DIR = os.path.join(AGENTS_DIR, "config")

    # 2. File Operations - Merge AGENTS.md
    print("Brain: absorbing system context...")
    root_agents_md = os.path.join(ROOT, "AGENTS.md")
    workflow_rules_md = os.path.join(RULES_DIR, "WORKFLOW_RULES.md")

    if os.path.exists(root_agents_md) and os.path.exists(workflow_rules_md):
        with open(root_agents_md, 'r') as f:
            agents_content = f.read()

        # Prepare content to prepend/insert
        with open(workflow_rules_md, 'r') as f:
            rules_content = f.read()

        # Prepend after title if possible
        lines = rules_content.splitlines()
        if lines and lines[0].startswith("# "):
            title = lines[0]
            rest = "\n".join(lines[1:])
            final_content = f"{title}\n\n## 0. System Context & Ingestion\n{agents_content}\n{rest}"
        else:
            final_content = f"## 0. System Context & Ingestion\n{agents_content}\n\n{rules_content}"

        with open(workflow_rules_md, 'w') as f:
            f.write(final_content)

        os.remove(root_agents_md)

    # 3. [Step Removed] Archiving system manual is now done manually before initialization.
    # We proceed directly to stamping the project.

    # 4. Update Project Manual (template_source/README.md)
    print("Brain: Stamping new project identity...")
    project_readme = os.path.join(DOCS_DIR, "USER_MANUAL.md")
    if os.path.exists(project_readme):
        # Update Title
        update_file(project_readme, r"^# \[Project Name\]", f"# {project_name}")
        # Add Badge
        badge = "> **Maintained by The Coding Squad. See .agents/docs/USER_MANUAL.md for commands.**\n\n"
        with open(project_readme, 'r') as f:
            content = f.read()
        # Insert after title
        lines = content.splitlines()
        if lines and lines[0].startswith("# "):
            lines.insert(1, "")
            lines.insert(2, badge)
        else:
            lines.insert(0, badge)
        with open(project_readme, 'w') as f:
            f.write("\n".join(lines))

    # 5. Update Configurations
    print("Brain: Tuning agent personas...")

    # Brain - Governance
    brain_config = os.path.join(CONFIG_DIR, "brain.md")
    update_file(brain_config, r"\*\*Current Mode:\*\* Democracy", f"**Current Mode:** {governance}")

    # Sentinel - Risk
    sentinel_config = os.path.join(CONFIG_DIR, "sentinel.md")
    with open(sentinel_config, 'r') as f:
        s_content = f.read()
    if "**Risk Tolerance:**" not in s_content:
        s_content = s_content.replace("**Role:** Security & Compliance.", f"**Role:** Security & Compliance.\n**Risk Tolerance:** {risk}")
        with open(sentinel_config, 'w') as f:
            f.write(s_content)

    # Boom - Project Context
    boom_config = os.path.join(CONFIG_DIR, "boom.md")
    with open(boom_config, 'r') as f:
        b_content = f.read()
    if "**Project Context:**" not in b_content:
        b_content = b_content.replace("**Role:** Feature Delivery.", f"**Role:** Feature Delivery.\n**Project Context:** {project_type}")
        with open(boom_config, 'w') as f:
            f.write(b_content)

    # 6. Unpack Template
    print("Brain: Unpacking project structure...")

    # Move everything from template_source to root
    for item in os.listdir(TEMPLATE_DIR):
        s = os.path.join(TEMPLATE_DIR, item)
        d = os.path.join(ROOT, item)
        if item == "scripts":
             # Handle scripts folder merging/moving carefully because we are running from it
             if os.path.exists(d):
                 # Merge contents
                 for subitem in os.listdir(s):
                     shutil.move(os.path.join(s, subitem), os.path.join(d, subitem))
                 os.rmdir(s) # should be empty now
             else:
                 shutil.move(s, d)
        else:
            if os.path.exists(d):
                # If destination exists (e.g. .gitignore or docs/), replace it.
                if os.path.isdir(d):
                    shutil.rmtree(d)
                else:
                    os.remove(d)
            shutil.move(s, d)

    # 7. Cleanup
    try:
        os.rmdir(TEMPLATE_DIR)
    except:
        pass # Might fail if not empty, but we moved everything.

    print("\n---------------------------------------------")
    print(f"✅ Brain: {project_name} initialized.")
    print(f"✅ Squad Governance: {governance}")
    print(f"✅ Security Level: {risk}")
    print("\nRun '/standup' or '/onboard' to begin working with the team.")

if __name__ == "__main__":
    main()
