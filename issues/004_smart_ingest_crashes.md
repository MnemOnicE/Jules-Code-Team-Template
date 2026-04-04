# Issue 4: Runtime Crashes in Memory Ingestion (`smart_ingest.py`)

## 1. Objective
Fix the `NameError` exceptions in `template_source/scripts/smart_ingest.py` caused by undefined variables, restoring the memory ingestion utility to a functional state. Additionally, standardize the output format to `.md` for better tool interoperability.

## 2. Context & Problem Statement
The `smart_ingest.py` script acts as the "Brain Initialization" system, responsible for maintaining digests of the codebase context. During the playtest, it crashed immediately while attempting to prune old files because several required string constants (`DIGEST_PREFIX`, `DELTA_PREFIX`, `INGEST_FILE_SUFFIX`) are not defined in the module scope.

Furthermore, while the original script used `.txt`, standardizing on `.md` improves interoperability with other LLM tools and aligns with the markdown-centric nature of the `PLAYTEST.md` feedback.

Reference: `PLAYTEST.md` and PR Review Feedback.

## 3. Scope of Work
*   **Target:** `template_source/scripts/smart_ingest.py`.
*   **Goal:** Define the missing constants correctly according to the intended architecture, convert existing `.txt` references to `.md`, and verify the pruning logic works as expected.

## 4. Execution Instructions

**Phase 1: Identify and Define Missing Variables**
1. Read `template_source/scripts/smart_ingest.py`.
2. Locate the function `prune_ingests(ingest_dir: str)`. It currently references `DIGEST_PREFIX` and `DELTA_PREFIX`.
3. Add the missing definitions to the constants block:
   ```python
   DIGEST_PREFIX = "digest_"
   DELTA_PREFIX = "delta_"
   INGEST_FILE_SUFFIX = ".md"
   ```

**Phase 2: Standardize on Markdown Extension**
1. Review the `run_ingest` function.
2. Change the string construction for `filename` to ensure both delta and full ingests use the `.md` extension.
3. Update the `main` function where it checks if the ingest directory is empty using `glob.glob(os.path.join(INGEST_DIR, "digest_*.txt"))` to instead search for `digest_*.md`.

**Phase 3: Review Pruning Logic**
1. Review the `prune_ingests` function. Ensure the `os.scandir` implementation correctly uses these variables (e.g., `if entry.name.startswith(DIGEST_PREFIX): ...`).

**Phase 4: Test & Verify**
1. Run `python template_source/scripts/smart_ingest.py`.
2. The script should complete without throwing a `NameError`.
3. Verify that the output digest files are created in the `ingests/` directory with a `.md` extension.

## 5. Definition of Done
* `smart_ingest.py` executes successfully top-to-bottom without throwing `NameError`.
* All output files strictly use the `.md` extension.
* The `prune_ingests` function correctly identifies and removes older files based on the defined prefixes and the `.md` suffix.
