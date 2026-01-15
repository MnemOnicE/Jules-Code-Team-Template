## 📚 Repository Context

This repository uses an automated ingestion system to maintain a snapshot of the codebase history.
Agents should check the `ingests/` directory for the latest codebase digest file (e.g., `digest_YYYYMMDD_HHMMSS.txt`).
Reading this file provides a comprehensive understanding of the project's state, structure, and content at that point in time.

The ingestion process is managed by `template_source/scripts/smart_ingest.py`, which is designed to run every 5 commits (or when the directory is empty), keeping only the latest 3 snapshots. It can also be forced via the `--force` flag for manual or emergency updates.
