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
    *   **IMPORTANT:** End your response with a clear "Plan of Action" for Phase 2.
    *   *Do not write the code yet.*

---

## PHASE 2: THE EXECUTION (Chat Generation 2)

**Trigger:** "Proceed with the implementation."

1.  **The Code:**
    *   **Scribe** or **Boom** must output the actual code block(s).
    *   Ensure filepaths are specified relative to the project root.

2.  **Memory Sync (Consolidated):**
    *   Append a brief summary of this session to `.jules/memory/history.md`.
    *   Update `.jules/memory/ROADMAP.md` if feature status changed.
    *   Do not overwrite entire files unless necessary.

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
