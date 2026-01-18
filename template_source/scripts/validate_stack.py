#!/usr/bin/env python3
import os
import re
import sys

# Configuration
TECH_STACK_PATH = "template_source/.agents/config/TECH_STACK.md"
SRC_DIR = "src"

# Hardcoded mapping for discrepancies between Human Name and Package Name
# This decouples documentation from implementation details.
PACKAGE_MAPPING = {
    "vue.js": "vue",
    "scikit-learn": "sklearn",
    "beautifulsoup4": "bs4",
    "pillow": "PIL",
}

# Standard Library Allowlist (Partial/Heuristic for Python 3.10)
# We prioritize system detection, but fallback to a set if needed.
try:
    STD_LIB = set(sys.stdlib_module_names)
except AttributeError:
    # Fallback for older python versions if ever run there, though 3.10 is specified
    STD_LIB = {
        "os", "sys", "re", "json", "math", "random", "datetime", "time", "typing",
        "collections", "itertools", "functools", "pathlib", "subprocess", "shutil",
        "logging", "argparse", "uuid", "hashlib", "base64", "io", "copy", "traceback",
        "inspect", "ast", "contextlib", "threading", "multiprocessing", "socket",
        "email", "http", "urllib", "xml", "html", "unittest", "doctest", "pydoc",
        "platform", "site", "sysconfig", "importlib", "zipfile", "tarfile", "csv",
        "sqlite3", "pickle", "shelve", "dbm", "tempfile", "glob", "fnmatch", "shlex"
    }

def normalize_name(name):
    """
    Normalizes a tech stack item name to a potential package name.
    Example: 'Vue.js' -> 'vuejs' (before mapping check)
             'FastAPI' -> 'fastapi'
    """
    # Remove version numbers if present (simple heuristic)
    name = re.sub(r'\s+\d+(\.\d+)*.*$', '', name)
    # Lowercase
    name = name.lower()
    # Check mapping first
    if name in PACKAGE_MAPPING:
        return PACKAGE_MAPPING[name]

    # Strip special chars for default normalization
    # We keep underscores as they are common in python packages
    normalized = re.sub(r'[^a-z0-9_]', '', name)
    return normalized

def parse_tech_stack(filepath):
    allowed_packages = set()

    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found. Skipping stack validation.")
        return set()

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            # Look for lines starting with '# -'
            if line.startswith('# -'):
                # Strip marker
                content = line[3:].strip()
                # Remove parenthetical notes e.g. "(Backend)"
                content = re.sub(r'\s*\(.*?\)', '', content).strip()

                if content:
                    # Handle multiple items? Usually one per line.
                    normalized = normalize_name(content)
                    allowed_packages.add(normalized)

                    # Also add the raw mapped version if the original input matches a key
                    if content.lower() in PACKAGE_MAPPING:
                        allowed_packages.add(PACKAGE_MAPPING[content.lower()])

    return allowed_packages

def get_imports_from_file(filepath):
    imports = set()
    ext = os.path.splitext(filepath)[1].lower()

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    if ext == '.py':
        # Regex for 'import X' or 'from X import Y'
        # Captures the top-level package name
        import_matches = re.findall(r'^(?:from|import)\s+([a-zA-Z0-9_]+)', content, re.MULTILINE)
        imports.update(import_matches)

    elif ext in ['.js', '.ts', '.vue']:
        # Regex for ES6 import
        # import ... from 'package'
        es6_matches = re.findall(r'import\s+.*?from\s+[\'"]([@a-zA-Z0-9_/-]+)[\'"]', content)
        imports.update(es6_matches)

        # Regex for CommonJS require
        # require('package')
        cjs_matches = re.findall(r'require\s*\(\s*[\'"]([@a-zA-Z0-9_/-]+)[\'"]\s*\)', content)
        imports.update(cjs_matches)

        # Filter out relative imports (starting with . or /)
        imports = {i for i in imports if not i.startswith('.') and not i.startswith('/')}

        # For scoped packages @org/pkg, usually we care about the whole thing,
        # but for normalization we might need to be careful.
        # For now, keep as is.

    return imports

def main():
    print("🛡️  Starting Semantic Firewall (Stack Validation)...")

    allowed_stack = parse_tech_stack(TECH_STACK_PATH)
    print(f"ℹ️  Allowed Stack (Normalized): {sorted(allowed_stack)}")

    # Add exceptions or implied packages
    # 'python' and 'javascript' are languages, not packages, but appear in stack.
    # We shouldn't flag them, but they aren't imports either.

    violations = []

    if not os.path.exists(SRC_DIR):
        print(f"ℹ️  Directory {SRC_DIR} does not exist. Nothing to scan.")
        return 0

    for root, dirs, files in os.walk(SRC_DIR):
        for file in files:
            if file.endswith(('.py', '.js', '.ts', '.vue')):
                filepath = os.path.join(root, file)
                file_imports = get_imports_from_file(filepath)

                for imp in file_imports:
                    # Clean up import name (handle 'pkg.subpkg')
                    root_pkg = imp.split('.')[0]

                    # Skip standard library (Python)
                    if root_pkg in STD_LIB:
                        continue

                    # Check if allowed
                    # We check both the root package and the full string just in case
                    # But usually allowlist matches root package.

                    # Normalization for comparison
                    norm_imp = normalize_name(root_pkg)

                    if norm_imp not in allowed_stack and root_pkg.lower() not in allowed_stack:
                        # Double check if it's a known language thing not in stdlib list
                        # e.g. if running in strict env.
                        violations.append((filepath, imp))

    if violations:
        print("\n🚨 CRITICAL: Semantic Firewall Breached! Found unauthorized imports:")
        for fp, imp in violations:
            print(f"  ❌  {fp}: Imports '{imp}' (Not in TECH_STACK.md)")
        print("\nAction: Add the library to .agents/config/TECH_STACK.md or remove the import.")
        sys.exit(1)
    else:
        print("\n✅  Semantic Firewall passes. No unauthorized hallucinations detected.")
        sys.exit(0)

if __name__ == "__main__":
    main()
