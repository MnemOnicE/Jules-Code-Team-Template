# ⌨️ Agent Command Interface (CLI)

The user may invoke these commands at the start of a prompt to trigger specific workflows immediately.

| Command | Workflow Trigger | Description |
| :--- | :--- | :--- |
| **/standup** `[topic]` | `workflows/standup.md` | **Brain** convenes the squad to debate architecture or features. |
| **/judge** `[code]` | `workflows/code_review.md` | **The Code Court.** Triggers Sentinel, Bolt, and Scribe to review input code. |
| **/test** | `workflows/qa.md` | **Scope's Gauntlet.** Generates 3 edge cases to break the current feature. |
| **/panic** | `workflows/incident.md` | **The War Room.** Bypasses debate. Fixes critical bugs immediately. |
| **/reflect** | `.jules/memory/TEAM_MEMORY.md` | **Scribe** forces a memory commit. Summarizes the session into the permanent log. |
| **/status** | `.jules/memory/ROADMAP.md` | **Brain** reports current active task and next planned items. |
| **/audit** | `workflows/audit.md` | **Brain** performs a full repository state analysis (Blueprint, Debt, Status, Reflect). |
| **/auto** | `workflows/autopilot.md` | **The Scout.** Brain scans the Roadmap and Memory to find the next best task automatically. |
| **/refactor** `[file]` | `workflows/refactor.md` | **The Janitor.** Bolt and Scribe clean up code without changing logic. |
| **/ship** `[ver]` | `workflows/release.md` | **The Release Manager.** Prepares changelogs and verifies builds. |
| **/explain** `[file]` | `workflows/explain.md` | **The Teacher.** Adds comments and explains complex logic. |
| **/design** `[idea]` | `workflows/design.md` | **The Architect.** Generates technical specs in `specs/` before coding. |
| **/heal** `[log]` | `workflows/heal.md` | **The Medic.** Autonomously diagnoses and patches errors. |
| **/manage** `[goal]` | `workflows/conductor.md` | **The Conductor.** Chains multiple protocols to solve complex goals. |
| **/sidebar** | `N/A` | **Break Character.** Drops all personas to answer queries directly and concisely. No logs. |
