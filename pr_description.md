🧪 [testing improvement] Add missing unit tests for toggle_defcon.py

🎯 **What:** The `template_source/scripts/toggle_defcon.py` script was previously untested, lacking verification for its critical function of renaming core configuration files to toggle the `boom` persona's operational status. This testing gap has been addressed.

📊 **Coverage:** The new test suite comprehensively covers all execution paths within the main script for both `emergency` and `normal` status arguments:
- **Happy Paths:** Validates the successful and correct invocation of `os.rename` when state changes are valid.
- **Redundant State Paths:** Ensures no changes are made and appropriate stdout messages are printed if the system is already in the requested state.
- **Error Paths:** Verifies that a `SystemExit` with code `1` is properly raised when target files are entirely missing.
All file system side effects are securely isolated via `unittest.mock.patch`.

✨ **Result:** Test coverage for this script is now established, providing a reliable safety net against regressions in the persona kill switch mechanism and ensuring the deterministic execution of the toggle logic.
