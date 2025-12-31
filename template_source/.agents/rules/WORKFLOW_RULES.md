# Agent Workflow Optimizations

This file provides instructions for the Coding Squad agents to optimize workflow, manage token usage, and reduce roleplay overhead.

## 1. The "Overkill" Issue (Too much debate for small tasks)
*   **Problem:** You don't need a 5-person philosophical debate to change a CSS color.
*   **Solution:** Use the **Autopilot / Scout Workflow**.
*   **Mechanism:** Triggered by `/auto` or generic "Go" prompts (`workflows/autopilot.md`).
*   **Instruction:** Brain immediately checks `memory/ROADMAP.md` or `memory/TEAM_MEMORY.md` for the next logical step and executes it, skipping the "User Input -> Contextualize -> Debate" cycle.
*   **Optimization:** Instruct Brain to "Run Autopilot on this specific small task" to bypass standup simulation.

## 2. The "Token Overhead" Issue (Context window exhaustion)
*   **Problem:** "Debate" and "Rebuttal" steps generate massive text, filling context windows.
*   **Solution:** Enforce the **Roll Call Limit**.
*   **Mechanism:** `workflows/standup.md` allows selecting "3-5 Agents most relevant".
*   **Instruction:** Limit Roll Call to exactly 2 agents (e.g., Bolt and Sentinel) for specific tasks to save tokens while maintaining adversarial quality.

## 3. The "Complexity" Issue (Getting lost in the roleplay)
*   **Problem:** Managing a simulated team of 8 is mentally taxing.
*   **Solution:** Use the **Conductor Workflow**.
*   **Mechanism:** Invoke `/manage [Complex Goal]` (`workflows/conductor.md`).
*   **Instruction:** Brain breaks the goal into phases (e.g., Phase 1: /design, Phase 2: /standup) and creates a "Playlist" in `memory/TEAM_MEMORY.md`. The AI acts in "Manager Mode," driving execution.

## 4. The "Emergency" Bypass (When functionality is broken)
*   **Problem:** Agents (esp. Sentinel) refuse to write code due to imperfections, blocking critical bug fixes.
*   **Solution:** Trigger the **War Room (Incident Workflow)**.
*   **Mechanism:** `/panic` or `workflows/incident.md`.
*   **Instruction:** Activates "Defcon 1". Boom is silenced (no feature creep). Scope and Orbit produce a "Direct fix applied immediately". Use for immediate patches.

## 5. The "Memory Flush" (Solving Token Limits)
*   **Problem:** Long conversations hit context limits.
*   **Solution:** Use the `/reflect` command.
*   **Mechanism:** `/reflect` triggers Scribe to "force a memory commit" in `memory/TEAM_MEMORY.md`.
*   **Instruction:** Run `/reflect` at the end of every significant coding session. Start new chats by reading `memory/TEAM_MEMORY.md`.

## 6. The "Surgical Strike" (Bypassing Debate)
*   **Problem:** Asking "How do I fix this?" triggers unnecessary debate.
*   **Solution:** Use `/heal` and `/refactor`.
*   **Mechanism:**
    *   `/heal [Error Log]`: Triggers Medic Workflow. Scope (Triage) -> Brain (Diagnosis) -> Boom (Surgery). Direct bug fix.
    *   `/refactor [file]`: Triggers Refactor Workflow. Scribe (Readability) + Bolt (Complexity). explicitly forbids changing external behavior.

## 7. The "Scope Check" (Preventing Feature Creep)
*   **Problem:** AI suggests "cool new ideas" distraction from the goal.
*   **Solution:** Use `/status`.
*   **Mechanism:** Brain checks `memory/ROADMAP.md` and reports "Active Feature" vs "Planned".
*   **Instruction:** Acts as a "grounding" command to force agents to stick to the roadmap.

## 8. The "System Anchor" (Fourth Wall Fix)
*   **Problem:** The agent structure seems lost or the Fourth Wall is broken.
*   **Solution:** Use `/reset`.
*   **Mechanism:** System reloads all definitions from `.agents/` and restarts the session context, retaining only the `memory/TEAM_MEMORY.md`.
*   **Instruction:** Invoke this if agents start acting like a generic chatbot.

## 9. The "Large Payload" Handling (Preventing System Bog)
*   **Problem:** User provides a massive file (e.g., >1MB or >2000 lines) which slows down processing and risks token limits.
*   **Solution:** Agents must check file size before reading.
*   **Instruction:** If a file is >1MB, agents must **default to requesting a summary** or using a script to analyze it, rather than ingesting the whole file.
*   **Exception:** This limit is not hard and fast. If the user explicitly requests a "Deep Dive" or "Full Analysis", or if the task strictly requires it, the agent may override this rule (potentially with a warning).

## 10. The Failover Rule
*   **Redundancy:** If `session.json` is unreadable, corrupted, or missing, Brain must default to ingesting `history.md` to rebuild the project state.
*   **Priority:** `session.json` is the primary source of truth for the machine; `history.md` is the immutable backup.

## Workflow Cheat Sheet

| Goal | Command | Why? |
| :--- | :--- | :--- |
| **Start a Task** | `/auto` or `/standup` | Let Brain decide the best agents for the job. |
| **Fix a Bug** | `/heal [paste error]` | Skips the debate; forces a direct code patch. |
| **Clean Code** | `/refactor [file]` | Optimizes code without changing logic/functionality. |
| **Save Context** | `/reflect` | Dumps memory to file so you can restart the chat. |
| **Emergency** | `/panic` | Bypasses everything for immediate fixes. |
| **Reset** | `/reset` | Reloads definitions and restarts session context. |
