# The Refactor Protocol 🧹

**Trigger:** User invokes `/refactor [file/dir]`

## STEP 1: THE AUDIT
* **Scribe:** Scan for readability, magic numbers, and missing comments.
* **Bolt:** Scan for cognitive complexity, performance bottlenecks, and redundant loops.
* **Sentinel:** Scan for security smells (even minor ones).

## STEP 2: THE PLAN
* **Brain:** Synthesize the complaints into a bulleted list of "Refactoring Targets".

## STEP 3: THE SWEEP
* **Boom:** Rewrite the code to address the targets.
* **CONSTRAINT:** **DO NOT** change the external behavior or logic of the code. Only structure/performance/clarity.
