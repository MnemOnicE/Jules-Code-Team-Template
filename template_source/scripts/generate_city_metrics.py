import os
import json
import sys

def count_lines(filepath):
    """Simple line counter (simplified cloc)."""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        return sum(1 for line in f if line.strip())

def generate_city_metrics(root_dir):
    """
    Traverses the directory and builds a metric tree.
    Each file is a 'building' with height = LOC.
    """
    city_data = {"name": "CodeCity", "children": []}

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip hidden directories and build artifacts
        if any(part.startswith('.') for part in dirpath.split(os.sep)):
            continue
        if 'node_modules' in dirpath or '__pycache__' in dirpath:
            continue

        for filename in filenames:
            if filename.endswith(('.py', '.js', '.ts', '.md', '.go', '.rs')):
                filepath = os.path.join(dirpath, filename)
                try:
                    loc = count_lines(filepath)
                    city_data["children"].append({
                        "name": filename,
                        "path": filepath,
                        "loc": loc,
                        "complexity": 1  # Placeholder for cyclomatic complexity
                    })
                except Exception as e:
                    print(f"Skipping {filename}: {e}", file=sys.stderr)

    return city_data

if __name__ == "__main__":
    metrics = generate_city_metrics(".")
    print(json.dumps(metrics, indent=2))
