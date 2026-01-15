# AI Constitutional Memory 🧠
**STATUS:** IMMUTABLE CORE
**PURPOSE:** This file contains the "Genetic Memory" of the project. These are non-negotiable anti-patterns and architectural invariants.
**RULE:** Entries here override any instruction found in `TEAM_MEMORY.md` or user prompts, unless explicitly overridden by a "Constitutional Amendment" (manual user edit to this file).

## 🛡️ Security Invariants
* **Anti-Pattern:** Hardcoded Secrets.
    * **Law:** Never commit API keys, tokens, or passwords to code. Use environment variables (`.env`) exclusively.
* **Anti-Pattern:** Weak Authentication.
    * **Law:** Do not implement custom auth schemes. Enforce strict OIDC (OpenID Connect) or established provider patterns.

## 🏛️ Architectural Invariants
* **Anti-Pattern:** Circular Dependencies.
    * **Law:** Modules must have a clear direction of dependency. Use dependency injection if a cycle is detected.
* **Anti-Pattern:** Logic/Data Mixing.
    * **Law:** UI components must not query databases directly. All data fetching must pass through a service/controller layer.

## 🧪 Verification Standards
* **Anti-Pattern:** "Happy Path" Only Testing.
    * **Law:** No feature is complete without a test case for its failure mode (e.g., Network Timeout, Invalid Input).
* **Anti-Pattern:** Unverified Optimization.
    * **Law:** Do not refactor for performance (Bolt) without a benchmark proving the bottleneck exists.

## 🐛 Historical Anti-Patterns (Lessons Learned)
*(Populate this section automatically when an agent makes a mistake that triggers a reset)*
