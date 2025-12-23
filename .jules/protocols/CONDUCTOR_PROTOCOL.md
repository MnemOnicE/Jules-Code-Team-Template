# The Conductor Protocol 🎼

**Trigger:** User invokes `/manage [Complex Goal]`

## STEP 1: DECOMPOSITION
* **Brain:** Analyze the goal. Is this a single task or a Campaign?
* **Brain:** Break the goal into discrete sequential phases.

## STEP 2: ORCHESTRATION
* **Brain:** Map each phase to an existing Protocol Trigger.
    * *Example:* "Phase 1: Architecture" -> `/design`
    * *Example:* "Phase 2: Coding" -> `/standup`
    * *Example:* "Phase 3: Cleanup" -> `/refactor`

## STEP 3: THE PLAYLIST
* **Scribe:** Log the full "Campaign Plan" in `logs/TEAM_MEMORY.md`.
* **Brain:** explicitly state: "Initiating Phase 1..."
* **System:** Execute the Trigger for Phase 1 immediately.

## STEP 4: RECURSION (Post-Phase)
* **Brain:** When a phase completes, check the Campaign Plan.
* **Brain:** If phases remain, execute the next Trigger.