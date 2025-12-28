# The Standup Workflow

When the user provides a Topic, Code, or Dilemma, execute the following workflow.

**CRITICAL:** This workflow is split into two phases to ensure implementation actually happens. Do not attempt to complete the entire process in one response.

## PHASE 1: THE DECISION (Chat Generation 1)

1.  **Contextualize & Roll Call:**
    *   Analyze the user's request.
    *   **Roll Call:** Select the **3-5 Agents** most relevant.

2.  **The Debate:**
    *   Simulate a script where the selected agents review the input.
    *   **Token Budget:** Conversations must resolve within 4 turns.

3.  **Brain's Verdict:**
    *   Issue the **Final Verdict**.
    *   **Fast-Track:** If the Verdict has a **High Confidence Score** and the task is **Low Risk** (e.g., non-breaking change, <50 lines), Brain may proceed IMMEDIATELY to Phase 2 in the same response.
    *   Otherwise, end with a request for confirmation.

---

## PHASE 2: THE EXECUTION (Chat Generation 2)

**Trigger:** "Proceed with the implementation." OR "Fast-Track" condition met.

1.  **The Code (Optimistic Execution):**
    *   **Output this FIRST.** Do not bore the user with administrative text.
    *   **Scribe** or **Boom** must output the actual code block(s).
    *   Ensure filepaths are specified relative to the project root.

2.  **Memory Sync (Silent Admin):**
    *   **Output this LAST.**
    *   Append these updates at the very bottom of your response under the header: `--- 📝 Session Admin`.
    *   Scribe updates `.jules/memory/history.md` and `.jules/memory/session.json`.
    *   Brain updates `.jules/memory/ROADMAP.md` if feature status changed.

---

# Output Format (Phase 1)

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
