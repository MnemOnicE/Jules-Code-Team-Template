# Scope's Gauntlet 🔬

**Objective:** Break the code before the user does. "Code is Truth; Text is Noise."

## Phase 1: The Red Test (Reproduction)
**Action:** Before any fix is attempted, you MUST prove the bug exists.
1.  Create a standalone script `tests/repro_issue.py`.
2.  This script must attempt to reproduce the reported issue or verify the absence of the requested feature.
3.  **Assert Failure:** The script MUST fail (exit code != 0) to confirm the issue is reproducible.
4.  If the script passes initially, the issue is invalid or not reproducible. Stop and report.

## Phase 2: The Fix
**Action:** The Implementer (Boom/Bolt) applies the fix or feature.
*   Do not modify the test script to make it pass.
*   Modify the source code to satisfy the test.

## Phase 3: The Green Test (Verification)
**Action:** Scope runs `tests/repro_issue.py` again.
1.  **Assert Success:** The script MUST now pass (exit code 0).
2.  **Cleanup:** Remove the temporary reproduction script unless instructed to keep it as a regression test.
3.  **Verdict:** Only AFTER the script passes can you verbally confirm "Fix Verified."
