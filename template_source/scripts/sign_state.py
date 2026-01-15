import hashlib
import json
import os
import sys

def sign_state():
    """
    Calculates a SHA-256 hash of the session.json file.
    This creates a cryptographic anchor for the current state, preventing
    drift between the machine state and the human narrative.
    """
    # Define possible paths for session.json relative to repo root
    possible_paths = [
        ".agents/memory/session.json",
        "template_source/.agents/memory/session.json"
    ]

    target_file = None
    for path in possible_paths:
        if os.path.exists(path):
            target_file = path
            break

    if not target_file:
        print("ERROR: session.json not found. State cannot be signed.")
        sys.exit(1)

    try:
        with open(target_file, 'rb') as f:
            file_content = f.read()

        # Calculate SHA-256 hash
        sha256_hash = hashlib.sha256(file_content).hexdigest()

        # Return the first 8 characters (Short Hash) for readability/logs
        # This is sufficient to detect if the file has changed between writes
        short_hash = sha256_hash[:8]
        print(f"{short_hash}")

    except Exception as e:
        print(f"ERROR: Could not sign state. {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    sign_state()
