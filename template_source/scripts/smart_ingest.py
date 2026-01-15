import os
import subprocess
import glob
from datetime import datetime
import shutil
import sys

INGEST_DIR = "ingests"

def get_commit_count():
    try:
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return int(result.stdout.strip())
    except subprocess.CalledProcessError:
        print("Error: Not a git repository or no commits found.")
        return 0

def run_ingest():
    os.makedirs(INGEST_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"digest_{timestamp}.txt"
    filepath = os.path.join(INGEST_DIR, filename)

    print(f"Running gitingest targeting '.' -> {filepath}")
    # gitingest . -o filepath
    try:
        subprocess.run(["gitingest", ".", "-o", filepath], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running gitingest: {e}")
        return

    prune_ingests()

def prune_ingests():
    # List all digest files
    files = glob.glob(os.path.join(INGEST_DIR, "digest_*.txt"))
    # Sort by modification time (or name, which has timestamp)
    # Using name is safer for order if modification times are weird, but creation time is best.
    # Since filename has timestamp, sorting by name is equivalent to sorting by time.
    files.sort()

    # Keep last 3
    if len(files) > 3:
        to_delete = files[:-3]
        for f in to_delete:
            print(f"Pruning old digest: {f}")
            os.remove(f)

def main():
    # Dependency Check
    if not shutil.which("gitingest"):
        print("❌ CRITICAL: `gitingest` not found. Memory updates disabled. Please install via pip.")
        sys.exit(1)

    commit_count = get_commit_count()

    # Check if ingest directory is empty
    is_empty = False
    if not os.path.exists(INGEST_DIR) or not glob.glob(os.path.join(INGEST_DIR, "digest_*.txt")):
        is_empty = True

    print(f"Commit count: {commit_count}")

    force_ingest = "--force" in sys.argv

    if commit_count % 5 == 0 or is_empty or force_ingest:
        if force_ingest:
            print("Force flag detected. Starting ingest...")
        else:
            print("Condition met (every 5th commit or empty). Starting ingest...")
        run_ingest()
    else:
        print("Skipping ingest (not 5th commit and not empty).")

if __name__ == "__main__":
    main()
