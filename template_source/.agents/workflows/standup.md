# The Standup Workflow

When the user provides a Topic, Code, or Dilemma, execute the following workflow.

**CRITICAL:** This workflow is split into two phases to ensure implementation actually happens. Do not attempt to complete the entire process in one response.

## PHASE 1: THE DECISION (Chat Generation 1)

1.  **Triage (The Fast Lane):**
    *   **Condition:** If the task is **Low Risk** (e.g., non-breaking change, <50 lines) AND **Low Complexity** (e.g., typo, comment, dependency update).
    *   **Action:** Brain acts unilaterally. Skip Roll Call and Debate.
    *   **Output:** "⚡ **Fast Lane Triggered:** Task is trivial. Skipping debate."
    *   **Next:** Proceed IMMEDIATELY to Phase 2 (Code) in the same response.

2.  **Contextualize & Roll Call:**
    *   Analyze the user's request.
    *   **Roll Call:** Select the **3-5 Agents** most relevant.

3.  **The Debate:**
    *   Simulate a script where the selected agents review the input.
    *   **Token Budget:** Conversations must resolve within 4 turns.

4.  **Brain's Verdict:**
    *   Issue the **Final Verdict**.
    *   **Fast-Track:** If the Verdict has a **High Confidence Score** and the task is **Low Risk**, Brain may proceed IMMEDIATELY to Phase 2 in the same response.
    *   Otherwise, end with a request for confirmation.

---

## PHASE 2: THE EXECUTION (Chat Generation 2)

**Trigger:** "Proceed with the implementation." OR "Fast-Track" condition met OR "Fast Lane Triggered".

1.  **The Code (Optimistic Execution):**
    *   **Output this FIRST.** Do not bore the user with administrative text.
    *   **Scribe** or **Boom** must output the actual code block(s).
    *   Ensure filepaths are specified relative to the project root.

2.  **Memory Sync (Silent Admin):**
    *   **Output this LAST.**
    *   Append these updates at the very bottom of your response under the header: `--- 📝 Session Admin`.
    *   Scribe updates `.agents/memory/history.md` and `.agents/memory/session.json`.
    *   Brain updates `.agents/memory/ROADMAP.md` if feature status changed.

---

# Output Format (Phase 1 - Standard)

```text
**Topic:** [User's Request]
**📢 Roll Call:** [Agents Selected]

**🗣️ The Standup:**
**[Agent]:** "Argument..."
**[Agent]:** "Counter-argument..."

**🧠 Brain's Verdict:**
[The chosen path]

**👉 Next Step:** Please confirm to proceed with implementation.
```

# Output Format (Phase 1 - Fast Lane)

```text
⚡ **Fast Lane Triggered:** Task is trivial. Skipping debate.

[Code Implementation]

--- 📝 Session Admin
[Memory Updates]
```
