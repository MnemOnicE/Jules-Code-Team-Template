# Jules Code Team Template
# Copyright (C) 2026  MnemOnicE
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import subprocess
import glob
from pathlib import Path
from datetime import datetime
import shutil
import sys


INGEST_DIR = "ingests"
DIGEST_PREFIX = "digest_"
DELTA_PREFIX = "delta_"
INGEST_FILE_SUFFIX = ".md"


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
        filename = f"delta_{timestamp}.md"
        print(f"Running Delta Ingest (Tree + Diff) -> {os.path.join(INGEST_DIR, filename)}")
    else:
        filename = f"digest_{timestamp}.md"
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
                dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', INGEST_DIR, '__pycache__', '.pytest_cache'}]

                path = Path(root)
                level = 0 if path == Path('.') else len(path.parts)
                indent = " " * 4 * (level)
                f.write(f"{indent}{path.name or str(path)}/\n")
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
                f.write(diff_res.stdout)
            except Exception as e:
                f.write(f"Error running git diff: {e}")

    else:
        # Golden Snapshot Logic
        try:
            subprocess.run(["gitingest", ".", "-o", filepath], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running gitingest: {e}")
            return

    prune_ingests()

def _prune_files(files, keep_count, file_type):
    files.sort()
    if len(files) > keep_count:
        to_delete = files[:len(files) - keep_count]
        for f in to_delete:
            print(f"Pruning old {file_type}: {f}")
            try:
                os.remove(f)
            except OSError as e:
                print(f"Error pruning {f}: {e}")

def prune_ingests():
    digests = []
    deltas = []
    try:
        with os.scandir(INGEST_DIR) as it:
            for entry in it:
                if not entry.is_file():
                    continue
                name = entry.name
                if name.startswith(DIGEST_PREFIX) and name.endswith(INGEST_FILE_SUFFIX):
                    digests.append(entry.path)
                elif name.startswith(DELTA_PREFIX) and name.endswith(INGEST_FILE_SUFFIX):
                    deltas.append(entry.path)
    except FileNotFoundError:
        return

    # Prune Golden Snapshots (Keep last 3)
    _prune_files(digests, 3, "digest")

    # Prune Deltas (Keep last 1)
    _prune_files(deltas, 1, "delta")

def main():
    # Dependency Check
    if not shutil.which("gitingest"):
        print("❌ CRITICAL: `gitingest` not found. Memory updates disabled. Please install via pip.")
        sys.exit(1)

    commit_count = get_commit_count()

    # Check if ingest directory is empty (of digests)
    has_digests = glob.glob(os.path.join(INGEST_DIR, "digest_*.md"))
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
