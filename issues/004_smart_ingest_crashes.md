# Issue 4: Runtime Crashes in Memory Ingestion (`smart_ingest.py`)

## 1. Objective
Fix the `NameError` exceptions in `template_source/scripts/smart_ingest.py` caused by undefined variables, restoring the memory ingestion utility to a functional state.

## 2. Context & Problem Statement
The `smart_ingest.py` script acts as the "Brain Initialization" system, responsible for maintaining digests of the codebase context. During the playtest, it crashed immediately while attempting to prune old files because several required string constants (`DIGEST_PREFIX`, `DELTA_PREFIX`, `INGEST_FILE_SUFFIX`) are not defined in the module scope.

Reference: `PLAYTEST.md`.

## 3. Scope of Work
*   **Target:** `template_source/scripts/smart_ingest.py`.
*   **Goal:** Define the missing constants correctly according to the intended architecture, and verify the pruning logic works as expected.

## 4. Execution Instructions

**Phase 1: Identify and Define Missing Variables**
1. Read `template_source/scripts/smart_ingest.py`.
2. Locate the function `prune_ingests(ingest_dir: str)`. It currently references `DIGEST_PREFIX` and `DELTA_PREFIX`.
3. Locate the constant definitions block at the top of the file.
4. Add the missing definitions. Based on typical context ingestion patterns, these should likely be:
   ```python
   DIGEST_PREFIX = "digest_"
   DELTA_PREFIX = "delta_"
   INGEST_FILE_SUFFIX = ".md" # Or .txt, based on how the files are written elsewhere
   ```
5. Ensure these prefixes align with how files are actually *named* during creation within the same script (check functions like `generate_digest` or wherever the output filename is constructed).

**Phase 2: Review Pruning Logic**
1. Review the `prune_ingests` function. Ensure the `os.scandir` implementation correctly uses these variables (e.g., `if entry.name.startswith(DIGEST_PREFIX): ...`).
2. Verify that there are no other undefined variables lurking in the execution paths.

**Phase 3: Test & Verify**
1. Run `python template_source/scripts/smart_ingest.py`.
2. The script should complete without throwing a `NameError`.
3. Verify that the output digest files are created in the `ingests/` directory.

## 5. Definition of Done
* `smart_ingest.py` executes successfully top-to-bottom without throwing `NameError`.
* The `prune_ingests` function correctly identifies and removes older files based on the newly defined prefixes.
