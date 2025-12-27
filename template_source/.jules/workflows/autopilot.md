# The Scout Workflow (Autopilot) 🔭

**Trigger:** User initiates "Autopilot" or provides no specific task.

## STEP 1: ROADMAP CHECK
**Brain** reads `ROADMAP.md`.
1.  **Is there an "Active" task?** -> **STOP.** Continue working on that task.
2.  **Is there a "Planned" task?** -> **STOP.** Select the top priority item.

## STEP 2: DEBT CHECK (If Roadmap is empty)
**Brain** reads `.jules/memory/TEAM_MEMORY.md`.
1.  **Are there unresolved "Reflections" or "Concerns"?** -> **STOP.** Select the most critical debt item (e.g., Bolt's performance complaint).

## STEP 3: THE HUNT (If Debt is clear)
**Brain** commands a random audit:
* **Orbit:** "Check the CI/CD pipeline configuration."
* **Sentinel:** "Audit `package.json` for outdated dependencies."
* **Bolt:** "Analyze the largest file in `src/` for complexity."
* **Scope:** "Generate a test case for a random function."

## STEP 4: HANDOFF
**Brain** passes the discovered task to **The Standup Workflow** with the message:
> "Autopilot discovered task: [Task Name]"
