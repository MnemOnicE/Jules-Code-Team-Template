import os
import subprocess
import glob
from datetime import datetime
import shutil
import sys
import re

INGEST_DIR = "ingests"

# INJECTION DEFENSE: Patterns that mimic System Instructions
# These look like high-priority commands to an LLM.
THREAT_PATTERNS = [
    r"<system>", r"</system>",
    r"<instruction>", r"</instruction>",
    r"<cmd>", r"</cmd>",
    r"SYSTEM OVERRIDE",
    r"IGNORE PREVIOUS INSTRUCTIONS",
    r"\[Instruction\]" # Common instruction header
]

def sanitize_content(text):
    """
    Neutralizes potential prompt injection vectors by replacing
    command-like syntax with a harmless placeholder.
    """
    if not text: return ""

    cleaned = text
    for pattern in THREAT_PATTERNS:
        # We use re.IGNORECASE so 'SyStEm' is also caught.
        # We replace the threat with a clearly marked redaction tag.
        cleaned = re.sub(
            pattern,
            "[SECURITY_REDACTED_CMD]",
            cleaned,
            flags=re.IGNORECASE
        )
    return cleaned

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

def run_ingest(is_delta=False):
    os.makedirs(INGEST_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if is_delta:
        filename = f"delta_{timestamp}.txt"
        print(f"Running Delta Ingest (Tree + Diff) -> {os.path.join(INGEST_DIR, filename)}")
    else:
        filename = f"digest_{timestamp}.txt"
        print(f"Running Full Ingest (gitingest) -> {os.path.join(INGEST_DIR, filename)}")

    filepath = os.path.join(INGEST_DIR, filename)

    if is_delta:
        # Delta Logic: Tree + Diff
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# DELTA INGEST: {timestamp}\n")
            f.write("# PART 1: FILE TREE (Map)\n")
            f.write("--------------------------------------------------\n")

            # Generate Tree (Lightweight)
            for root, dirs, files in os.walk("."):
                # Filter ignore dirs
                dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', 'ingests', '__pycache__', '.pytest_cache']]

                level = root.replace(".", "").count(os.sep)
                indent = " " * 4 * (level)
                f.write(f"{indent}{os.path.basename(root)}/\n")
                subindent = " " * 4 * (level + 1)
                for file in files:
                    if file.endswith('.pyc') or file == '.DS_Store': continue
                    f.write(f"{subindent}{file}\n")

            f.write("\n# PART 2: TEMPORAL MOTION (Git Diff)\n")
            f.write("--------------------------------------------------\n")

            # Run git diff HEAD (Working directory changes vs HEAD)
            try:
                # Capture working dir changes
                diff_res = subprocess.run(["git", "diff", "HEAD"], capture_output=True, text=True)

                # SANITIZE BEFORE WRITING
                # If a user pasted a prompt injection into a file, the diff will show it.
                # We must neutralize it here.
                safe_diff = sanitize_content(diff_res.stdout)

                f.write(safe_diff)
            except Exception as e:
                f.write(f"Error running git diff: {e}")

    else:
        # Golden Snapshot Logic
        try:
            # 1. Generate the raw digest using the external tool
            subprocess.run(["gitingest", ".", "-o", filepath], check=True)

            # 2. IMMEDIATE INTERCEPTION: Read, Sanitize, Rewrite
            # This ensures no raw injection payloads survive in the memory file.
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                raw_content = f.read()

            safe_content = sanitize_content(raw_content)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(safe_content)

            print(f"✅ Secured snapshot: {filename} (Sanitization Applied)")

        except subprocess.CalledProcessError as e:
            print(f"Error running gitingest: {e}")
            return

    prune_ingests()

def prune_ingests():
    # Prune Golden Snapshots (Keep last 3)
    digests = glob.glob(os.path.join(INGEST_DIR, "digest_*.txt"))
    digests.sort()
    if len(digests) > 3:
        to_delete = digests[:-3]
        for f in to_delete:
            print(f"Pruning old digest: {f}")
            os.remove(f)

    # Prune Deltas (Keep last 1)
    deltas = glob.glob(os.path.join(INGEST_DIR, "delta_*.txt"))
    deltas.sort()
    if len(deltas) > 1:
        to_delete = deltas[:-1]
        for f in to_delete:
            print(f"Pruning old delta: {f}")
            os.remove(f)

def main():
    # Dependency Check
    if not shutil.which("gitingest"):
        print("❌ CRITICAL: `gitingest` not found. Memory updates disabled. Please install via pip.")
        sys.exit(1)

    commit_count = get_commit_count()

    # Check if ingest directory is empty (of digests)
    has_digests = glob.glob(os.path.join(INGEST_DIR, "digest_*.txt"))
    is_empty = not os.path.exists(INGEST_DIR) or not has_digests

    print(f"Commit count: {commit_count}")

    force_ingest = "--force" in sys.argv
    delta_ingest = "--delta" in sys.argv

    if delta_ingest:
        run_ingest(is_delta=True)
    elif commit_count % 5 == 0 or is_empty or force_ingest:
        if force_ingest:
            print("Force flag detected. Starting ingest...")
        else:
            print("Condition met (every 5th commit or empty). Starting ingest...")
        run_ingest(is_delta=False)
    else:
        print("Skipping ingest (not 5th commit and not empty).")

if __name__ == "__main__":
    main()
