# The Release Protocol 🚢

**Trigger:** User invokes `/ship [version]`

## STEP 1: PRE-FLIGHT CHECK
* **Scope:** Simulate a "Happy Path" user session. Does the app actually run?
* **Orbit:** audit `package.json` version, ensure `npm run build` (or equivalent) config is sound.

## STEP 2: DOCUMENTATION
* **Scribe:** Read `logs/STANDUP_HISTORY.md` and `logs/TEAM_MEMORY.md`.
* **Scribe:** Draft a `CHANGELOG.md` entry summarizing recent changes.

## STEP 3: VERDICT
* **Brain:** Issue a **GO** or **NO-GO** decision for deployment.
