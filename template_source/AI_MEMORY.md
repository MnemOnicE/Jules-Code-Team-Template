# AI Memory

This file serves as a **mutable knowledge base** for all agents working on this project. It persists across sessions to prevent repetitive errors and document project-specific patterns.

## 🧠 Learnings & Patterns

### [2026-02-18] Security: Command Injection in Node.js Scripts
*   **Context**: Use of `child_process.execSync` with template literals containing filenames allowed command injection via malicious filenames.
*   **Solution**: Replaced `execSync` with `execFileSync` and passed arguments as an array. This avoids shell interpretation and prevents injection.
*   **Anti-Pattern**: Using `execSync` (or other shell-invoking functions) with unsanitized user-controllable input or filenames.

### [YYYY-MM-DD] Pattern: <Title>
*   **Context**: What was the problem?
*   **Solution**: How was it solved?
*   **Anti-Pattern**: What should be avoided?

## 🐛 Bug Workarounds

### [YYYY-MM-DD] Bug: <Title>
*   **Root Cause**: ...
*   **Workaround**: ...
*   **Fix Status**: (Pending/Resolved)

## 🔧 Environment Quirks
*   ...
