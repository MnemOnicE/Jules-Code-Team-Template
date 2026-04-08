# The Audit Workflow

When the user runs `/audit`, **Brain** performs a comprehensive review of the repository state.

## STEP 1: BLUEPRINT (Architecture Map)
*   **Brain** analyzes the file structure (`tree` or `ls -R`).
*   Map the high-level architecture.
*   Identify key modules, entry points, and data flow.
*   **Output:** A high-level description of the system's "shape".

## STEP 2: DEBT (Crack Finding)
*   **Brain** (optionally invoking **Bolt** or **Sentinel**) scans for:
    *   `TODO` or `FIXME` comments.
    *   Empty files or directories.
    *   Missing documentation or types.
    *   Security vulnerabilities or outdated dependencies.
*   **Output:** A bulleted list of "Cracks" or "Technical Debt" items.

## STEP 3: STATUS (Timeline Report)
*   **Brain** checks `.agents/memory/ROADMAP.md` and `.agents/memory/history.md`.
*   Determine the current phase (e.g., "Prototyping", "MVP", "Scaling").
*   Compare "Planned" vs. "Completed" tasks.
*   **Output:** A status summary (On Track, Behind, Blocked).

## STEP 4: REFLECT (Memory Commit)
*   **Scribe** summarizes the Audit findings.
*   Update `.agents/memory/TEAM_MEMORY.md` with the audit results.
*   **Memory Compression Rule:** When `TEAM_MEMORY.md` exceeds 50 lines, **Scribe** must perform a "Garbage Collection": Summarize the oldest "Reflections" into a single "Context" paragraph and delete the raw logs.
*   **Output:** A confirmation that the audit has been logged.

---

# Output Format

```text
**📋 AUDIT REPORT**

**🏗️ BLUEPRINT (Architecture)**
*   **Root:** [Description]
*   **Modules:** [List of key modules]
*   **Flow:** [Brief data flow description]

**🏚️ DEBT (Findings)**
*   [ ] [Criticality] [Issue Description]
*   [ ] [Criticality] [Issue Description]

**⏱️ STATUS (Timeline)**
*   **Phase:** [Current Phase]
*   **Progress:** [Completed/Total] tasks.
*   **Verdict:** [On Track / Behind / Blocked]

**💾 REFLECTION**
*   Logged to `.agents/memory/TEAM_MEMORY.md`.
```
