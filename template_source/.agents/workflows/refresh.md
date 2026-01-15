# The Refresh Workflow 🔄

**Trigger:** Slash Command `/refresh`

## Purpose
Manually trigger the code ingestion script to ensure the Agent's context is perfectly synced with the codebase state.

## Execution Steps

1.  **Brain's Announcement:**
    *   State: "Updating codebase digest..."

2.  **The Trigger:**
    *   Run the bash command: `python scripts/smart_ingest.py --force`

3.  **Confirmation:**
    *   Once the script completes, confirm the new digest has been created in `ingests/`.
    *   State: "Eyes open. I see the latest changes."
