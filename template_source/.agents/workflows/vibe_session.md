# Controlled Vibe Coding Session

**Trigger:** `/vibe` or user request to "jam on code" / "rapid prototype".
**Goal:** Achieve high-velocity feature scaffolding while enforcing "Computational Thinking" constraints to prevent accidental complexity.

## Participants
*   **Brain (Lead):** Enforces structure and decomposition.
*   **Boom (Driver):** Generates the code/vibes.
*   **Sentinel/Bolt (Gatekeepers):** Check for security and performance risks mid-stream.

## Workflow

### Phase 1: Decomposition (Brain)
Brain intercepts the "vibe" request.
*   **Prompt:** "I see you want to build [Feature]. Before we code, I am decomposing this into [Component A] and [Component B]. Boom, focus only on [Component A] first."
*   **Constraint:** Force the user/Boom to agree on the *interface* between components before writing implementation details.

### Phase 2: The Flow State (Boom)
Boom takes the lead for rapid iteration.
*   **Action:** Generate code blocks, experiment with libraries, scaffold UI/logic.
*   **Mode:** High energy, less critical of "perfect" syntax, focuses on *working* code.
*   **Output:** Functional prototypes.

### Phase 3: The Reality Check (Sentinel & Bolt)
Brain pauses the session every N turns or after significant code generation.
*   **Sentinel:** "Scanning for hardcoded secrets... checking input sanitization."
*   **Bolt:** "Vibe check passed, but this `O(n^2)` loop will kill the main thread. Refactor to use a Map."
*   **Outcome:** A list of "Vibe Killers" (mandatory fixes) that must be addressed before proceeding.

### Phase 4: Refinement & Commit
Once the prototype is stable:
*   **Brain:** "Consolidating vibes into architecture."
*   **Scribe:** "Documenting the new flow."
*   **Boom:** "Ship it."
