# Deep Security Audit (Attacker's Mindset)

**Trigger:** `/audit` or before major release.
**Goal:** Simulate a hostile attack on the codebase to find vulnerabilities, logic flaws, and architectural weaknesses.

## Participants
*   **Sentinel (Lead):** The Attacker.
*   **Scope (Support):** The Formal Verifier.
*   **Brain (Judge):** Assesses risk severity.

## Workflow

### Phase 1: Threat Modeling (Sentinel)
Sentinel analyzes the architecture.
*   **Question:** "Where is the data? Where is the money/value? Who are the actors?"
*   **Output:** A list of attack vectors (e.g., "API Endpoint X", "Smart Contract Y", "User Session Z").

### Phase 2: The Attack (Sentinel)
For each vector, Sentinel simulates an exploit.
*   **Secrets Check:** Scans for git-secrets, env vars in code.
*   **Logic Check:** "What if I withdraw 0? What if I withdraw negative? What if I call this function twice?" (Re-entrancy/Overflow).
*   **Identity Check:** "Are we using long-lived keys? Can I spoof the workload identity?" (SPIFFE check).

### Phase 3: Formal Verification (Scope)
For critical state logic identified by Sentinel.
*   **Action:** Scope attempts to describe the logic in pseudo-TLA+ or state tables.
*   **Goal:** Prove that an invalid state is reachable.
*   **Output:** "Counter-example found" or "Model holds".

### Phase 4: Remediation
Brain prioritizes the findings.
*   **Critical:** Immediate fix required.
*   **Warning:** Technical debt ticket.
*   **Info:** Documentation update.
