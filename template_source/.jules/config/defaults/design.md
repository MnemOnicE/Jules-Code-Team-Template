# The Architect Workflow 📐

**Trigger:** User invokes `/design [Concept]`

## STEP 1: REQUIREMENTS
* **Brain:** Convert the user's concept into a specific "User Story".
* **Palette:** Define the UI/UX requirements needed to support this story.

## STEP 2: CONSTRAINTS
* **Sentinel:** Define security requirements (Auth, RBAC, Data Validation).
* **Bolt:** Define performance limits (Max rows, Caching strategy).

## STEP 3: THE BLUEPRINT
* **Scribe:** Create a new file in `specs/` (e.g., `specs/referral_system.md`).
* **Scribe:** Write the full Technical Spec: Data Models, API Endpoints, and Component Tree.

## STEP 4: APPROVAL
* **Brain:** Ask the user: "Blueprint generated in `specs/`. Shall we proceed to implementation?"