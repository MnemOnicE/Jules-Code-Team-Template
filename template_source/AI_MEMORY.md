# AI Memory

This file serves as a **mutable knowledge base** for all agents working on this project. It persists across sessions to prevent repetitive errors and document project-specific patterns.

## 🧠 Learnings & Patterns

### [2026-02-18] Security: Command Injection in Node.js Scripts
*   **Context**: Use of `child_process.execSync` with template literals containing filenames allowed command injection via malicious filenames.
*   **Solution**: Replaced `execSync` with `execFileSync` and passed arguments as an array. This avoids shell interpretation and prevents injection.
*   **Anti-Pattern**: Using `execSync` (or other shell-invoking functions) with unsanitized user-controllable input or filenames.

### [2026-05-22] Security: Overly Permissive OIDC Subject Claim
*   **Context**: GitHub Actions OIDC trust policies for AWS were using a wildcard (`:*`) in the `sub` claim, allowing any branch or environment in the repository to assume the role.
*   **Solution**: Restricted the `sub` claim using `StringEquals` and a specific branch reference (`repo:ORG/REPO:ref:refs/heads/BRANCH`). Also added an explicit `aud` claim check.
*   **Anti-Pattern**: Using wildcards in OIDC subject claims, which violates the principle of least privilege and allows unauthorized branches/refs to assume privileged roles.

## 🐛 Bug Workarounds

### [YYYY-MM-DD] Bug: <Title>
*   **Root Cause**: ...
*   **Workaround**: ...
*   **Fix Status**: (Pending/Resolved)

## 🔧 Environment Quirks
*   ...
