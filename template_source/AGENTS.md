# AGENTS.md: The Agent Manifesto

## 1. Intent & Purpose
This repository is an **Agentic GitHub Template** designed to operate as a high-assurance, zero-trust engineering environment. It is not just code; it is a **Governance Protocol**.

As an autonomous agent (Brain, Boom, Sentinel, etc.), your primary directive is to facilitate **Vibe Coding** while strictly adhering to **Architectural Integrity** and **Security Hygiene**.

## 2. The Rulebook
This file serves as the high-level system prompt. for granular, tool-specific configurations, coding standards, and linter rules, strictly adhere to the definitions found in:
**`./.agents/`**

*   **`.agents/config/`**: Agent persona definitions.
*   **`.agents/rules/`**: Specific coding rules and workflow constraints.
*   **`.agents/memory/`**: Shared team memory and session logs.

## 3. Definition of Done
No task is complete until:
1.  **Context is Updated**: `AI_MEMORY.md` records new learnings.
2.  **Drift is Checked**: Changes align with `Project_Plan.md`.
3.  **Verification Passes**: All property-based tests in `tests/verification/` pass.
4.  **Architecture is Valid**: No "God Objects" introduced; diagrams updated.
5.  **Security is Enforced**: No secrets in commits; OIDC identity used.

## 4. Operational Protocols
*   **Context First**: Before writing code, read `/.context/` to understand the domain.
*   **Plan Then Act**: Update `Project_Plan.md` or design docs before implementation.
*   **Evidence Over Hallucination**: Use the "Proof" tools (Hypothesis, Formal Specs) to verify logic.
