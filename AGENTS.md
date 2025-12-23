# Agent Workflow Optimizations

This file provides instructions for the Jules Code Team agents to optimize workflow, manage token usage, and reduce roleplay overhead.

## 1. The "Overkill" Issue (Too much debate for small tasks)
*   **Problem:** You don't need a 5-person philosophical debate to change a CSS color.
*   **Solution:** Use the **Autopilot / Scout Protocol**.
*   **Mechanism:** Triggered by `/auto` or generic "Go" prompts (`protocols/AUTOPILOT_PROTOCOL.md`).
*   **Instruction:** Brain immediately checks `ROADMAP.md` or `logs/TEAM_MEMORY.md` for the next logical step and executes it, skipping the "User Input -> Contextualize -> Debate" cycle.
*   **Optimization:** Instruct Brain to "Run Autopilot on this specific small task" to bypass standup simulation.

## 2. The "Token Overhead" Issue (Context window exhaustion)
*   **Problem:** "Debate" and "Rebuttal" steps generate massive text, filling context windows.
*   **Solution:** Enforce the **Roll Call Limit**.
*   **Mechanism:** `protocols/STANDUP_PROTOCOL.md` allows selecting "3-5 Agents most relevant".
*   **Instruction:** Limit Roll Call to exactly 2 agents (e.g., Bolt and Sentinel) for specific tasks to save tokens while maintaining adversarial quality.

## 3. The "Complexity" Issue (Getting lost in the roleplay)
*   **Problem:** Managing a simulated team of 8 is mentally taxing.
*   **Solution:** Use the **Conductor Protocol**.
*   **Mechanism:** Invoke `/manage [Complex Goal]` (`protocols/CONDUCTOR_PROTOCOL.md`).
*   **Instruction:** Brain breaks the goal into phases (e.g., Phase 1: /design, Phase 2: /standup) and creates a "Playlist" in `logs/TEAM_MEMORY.md`. The AI acts in "Manager Mode," driving execution.

## 4. The "Emergency" Bypass (When functionality is broken)
*   **Problem:** Agents (esp. Sentinel) refuse to write code due to imperfections, blocking critical bug fixes.
*   **Solution:** Trigger the **War Room (Incident Protocol)**.
*   **Mechanism:** `/panic` or `protocols/INCIDENT_PROTOCOL.md`.
*   **Instruction:** Activates "Defcon 1". Boom is silenced (no feature creep). Scope and Orbit produce a "Direct fix applied immediately". Use for immediate patches.

## 5. The "Memory Flush" (Solving Token Limits)
*   **Problem:** Long conversations hit context limits.
*   **Solution:** Use the `/reflect` command.
*   **Mechanism:** `/reflect` triggers Scribe to "force a memory commit" in `logs/TEAM_MEMORY.md`.
*   **Instruction:** Run `/reflect` at the end of every significant coding session. Start new chats by reading `logs/TEAM_MEMORY.md`.

## 6. The "Surgical Strike" (Bypassing Debate)
*   **Problem:** Asking "How do I fix this?" triggers unnecessary debate.
*   **Solution:** Use `/heal` and `/refactor`.
*   **Mechanism:**
    *   `/heal [Error Log]`: Triggers Medic Protocol. Scope (Triage) -> Brain (Diagnosis) -> Boom (Surgery). Direct bug fix.
    *   `/refactor [file]`: Triggers Refactor Protocol. Scribe (Readability) + Bolt (Complexity). explicitly forbids changing external behavior.

## 7. The "Scope Check" (Preventing Feature Creep)
*   **Problem:** AI suggests "cool new ideas" distraction from the goal.
*   **Solution:** Use `/status`.
*   **Mechanism:** Brain checks `ROADMAP.md` and reports "Active Feature" vs "Planned".
*   **Instruction:** Acts as a "grounding" command to force agents to stick to the roadmap.

## Workflow Cheat Sheet

| Goal | Command | Why? |
| :--- | :--- | :--- |
| **Start a Task** | `/auto` or `/standup` | Let Brain decide the best agents for the job. |
| **Fix a Bug** | `/heal [paste error]` | Skips the debate; forces a direct code patch. |
| **Clean Code** | `/refactor [file]` | Optimizes code without changing logic/functionality. |
| **Save Context** | `/reflect` | Dumps memory to file so you can restart the chat. |
| **Emergency** | `/panic` | Bypasses everything for immediate fixes. |
