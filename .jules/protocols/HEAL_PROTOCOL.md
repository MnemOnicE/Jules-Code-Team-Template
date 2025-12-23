# The Medic Protocol 🚑

**Trigger:** User invokes `/heal [Error Log]`

## STEP 1: TRIAGE
* **Scope:** Analyze the stack trace. Identify the file and line number causing the crash.
* **Scope:** Is this a Logic Error, Syntax Error, or Environment Error?

## STEP 2: DIAGNOSIS
* **Brain:** Explain *why* the code failed. (e.g., "Null pointer exception because X was undefined").

## STEP 3: SURGERY
* **Boom:** Write the specific code patch to fix the error.
* **Sentinel:** Ensure the fix doesn't open a security hole.

## STEP 4: POST-OP
* **Scribe:** Log the incident resolution in `logs/TEAM_MEMORY.md`.