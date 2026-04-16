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
import json
import sys

try:
    import lizard
except ImportError:
    lizard = None

def count_lines(filepath):
    """Simple line counter (simplified cloc)."""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        return sum(1 for line in f if line.strip())

def get_complexity(filepath):
    """Calculates cyclomatic complexity using lizard."""
    if not lizard:
        return 1

    # Lizard doesn't support Markdown, return 1 as base complexity
    if filepath.endswith('.md'):
        return 1

    try:
        analysis = lizard.analyze_file(filepath)
        # Use CCN (Cyclomatic Complexity Number) which is sum of function complexities
        # If no functions (e.g. script), it returns 0. Default to 1.
        return max(analysis.CCN, 1)
    except Exception as e:
        print(f"Complexity error for {filepath}: {e}", file=sys.stderr)
        return 1

def generate_city_metrics(root_dir):
    """
    Traverses the directory and builds a metric tree.
    Each file is a 'building' with height = LOC.
    """
    city_data = {"name": "CodeCity", "children": []}

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Prune hidden directories and build artifacts
        # Modifying dirnames in-place prunes the search tree for os.walk
        dirnames[:] = [d for d in dirnames if not d.startswith('.') and d not in ('node_modules', '__pycache__')]

        for filename in filenames:
            if filename.endswith(('.py', '.js', '.ts', '.md', '.go', '.rs')):
                filepath = os.path.join(dirpath, filename)
                try:
                    loc = count_lines(filepath)
                    complexity = get_complexity(filepath)
                    city_data["children"].append({
                        "name": filename,
                        "path": filepath,
                        "loc": loc,
                        "complexity": complexity
                    })
                except Exception as e:
                    print(f"Skipping {filename}: {e}", file=sys.stderr)

    return city_data

if __name__ == "__main__":
    if len(sys.argv) > 1:
        root = sys.argv[1]
    else:
        root = "."

    metrics = generate_city_metrics(root)
    print(json.dumps(metrics, indent=2))
