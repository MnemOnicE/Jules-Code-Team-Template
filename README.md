# [Project Name]

## 🛠️ Built by The Coding Squad
This project is managed by the **Jules Code Team** template.

## 🚦 Status
* **Active Feature:** (See `ROADMAP.md`)
* **Latest Log:** (See `logs/STANDUP_HISTORY.md`)

## ⚡ Quick Start

### 1. Initialize the Squad
Run the onboarding script to configure your team, set governance, and unpack the project structure.
*(Requires Python 3+. No external dependencies or installation needed).*
```bash
python template_source/scripts/init_project.py
```

### 2. Start Working
Once initialized, use the slash commands below to interact with the squad.

## ⌨️ Quick Reference / Controls
| Command | Protocol Trigger | Description |
| :--- | :--- | :--- |
| **/standup** `[topic]` | `protocols/STANDUP_PROTOCOL.md` | **Brain** convenes the squad to debate architecture or features. |
| **/judge** `[code]` | `protocols/CODE_REVIEW_PROTOCOL.md` | **The Code Court.** Triggers Sentinel, Bolt, and Scribe to review input code. |
| **/test** | `protocols/QA_PROTOCOL.md` | **Scope's Gauntlet.** Generates 3 edge cases to break the current feature. |
| **/panic** | `protocols/INCIDENT_PROTOCOL.md` | **The War Room.** Bypasses debate. Fixes critical bugs immediately. |
| **/reflect** | `logs/TEAM_MEMORY.md` | **Scribe** forces a memory commit. Summarizes the session into the permanent log. |
| **/status** | `ROADMAP.md` | **Brain** reports current active task and next planned items. |
| **/audit** | `protocols/AUDIT_PROTOCOL.md` | **Brain** performs a full repository state analysis (Blueprint, Debt, Status, Reflect). |
| **/auto** | `protocols/AUTOPILOT_PROTOCOL.md` | **The Scout.** Brain scans the Roadmap and Memory to find the next best task automatically. |
| **/refactor** `[file]` | `protocols/REFACTOR_PROTOCOL.md` | **The Janitor.** Bolt and Scribe clean up code without changing logic. |
| **/ship** `[ver]` | `protocols/RELEASE_PROTOCOL.md` | **The Release Manager.** Prepares changelogs and verifies builds. |
| **/explain** `[file]` | `protocols/EXPLAIN_PROTOCOL.md` | **The Teacher.** Adds comments and explains complex logic. |
| **/design** `[idea]` | `protocols/DESIGN_PROTOCOL.md` | **The Architect.** Generates technical specs in `specs/` before coding. |
| **/heal** `[log]` | `protocols/HEAL_PROTOCOL.md` | **The Medic.** Autonomously diagnoses and patches errors. |
| **/manage** `[goal]` | `protocols/CONDUCTOR_PROTOCOL.md` | **The Conductor.** Chains multiple protocols to solve complex goals. |
| **/sidebar** | `N/A` | **Break Character.** Drops all personas to answer queries directly and concisely. No logs. |
