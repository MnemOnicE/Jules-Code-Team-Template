# Product Launch (From Project to Product)

**Trigger:** `/launch` or `/ship`.
**Goal:** Prepare the codebase for public release or production deployment, ensuring legal, commercial, and technical readiness.

## Participants
*   **Orbit (Lead):** Release Manager.
*   **Scope (QA):** Final Validation.
*   **Scribe (Docs):** Artifact Generation.

## Workflow

### Phase 1: MVP Validation (Orbit)
Orbit checks if the "Product" meets the "Minimum Viable" definition.
*   **Check:** Does it solve the core user problem?
*   **Check:** Is the "Happy Path" bug-free? (Scope verifies).
*   **Check:** Are we over-engineering? (Strip non-essential microservices).

### Phase 2: License & Governance (Orbit)
Orbit audits the open-source status.
*   **Decision:** "What license are we shipping with?" (GPL / Apache / EPL).
*   **Compatibility:** "Are we using GPL libraries in a closed-source product?" (Compliance check).
*   **Strategy:** "Is this Open Core? What features are paid?"

### Phase 3: Artifact Generation (Scribe)
Scribe prepares the release materials.
*   **CHANGELOG:** Summarize commits.
*   **README:** Update with "Getting Started".
*   **Docs:** Ensure "Documentation as Code" is built and linked.

### Phase 4: The Button (Brain)
Brain gives the final GO/NO-GO.
*   **GO:** Orbit tags the release (`git tag v1.0.0`) and pushes.
*   **NO-GO:** Return to development.
