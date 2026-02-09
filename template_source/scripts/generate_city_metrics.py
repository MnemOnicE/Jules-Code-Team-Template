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
