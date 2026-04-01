import timeit
import sys
import os
import shutil
import tempfile
from pathlib import Path

# Add scripts to path
scripts_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "template_source", "scripts"))
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

import validate_stack

def setup_dummy_src(target_dir):
    """Creates a large dummy directory structure."""
    src_path = Path(target_dir) / "src"
    src_path.mkdir(parents=True, exist_ok=True)

    for i in range(10):
        subdir = src_path / f"pkg_{i}"
        subdir.mkdir()
        for j in range(10):
            (subdir / f"module_{j}.py").write_text("import os\nimport sys\n")

        # Add __pycache__ with many files
        pycache = subdir / "__pycache__"
        pycache.mkdir()
        for j in range(50):
            (pycache / f"module_{j}.cpython-310.pyc").write_text("dummy bytecode")

def benchmark():
    with tempfile.TemporaryDirectory() as tmpdir:
        original_cwd = os.getcwd()
        os.chdir(tmpdir)
        try:
            setup_dummy_src(tmpdir)

            # Mock TECH_STACK_PATH for validate_stack
            os.makedirs("template_source/.agents/config", exist_ok=True)
            with open("template_source/.agents/config/TECH_STACK.md", "w") as f:
                f.write("# - python\n# - os\n# - sys\n")

            # Use the SRC_DIR from the module
            validate_stack.SRC_DIR = "src"
            validate_stack.TECH_STACK_PATH = "template_source/.agents/config/TECH_STACK.md"

            number = 100

            # We wrap the main logic or the specific loop to benchmark
            # Since main() has prints and sys.exit, let's benchmark a function that does the walk

            allowed_stack = validate_stack.parse_tech_stack(validate_stack.TECH_STACK_PATH)

            def run_validation():
                # Mimic the loop in main()
                violations = []
                for root, dirs, files in os.walk(validate_stack.SRC_DIR):
                    # Prune directories in-place to avoid traversing into non-source folders
                    dirs[:] = [d for d in dirs if d not in {'__pycache__', 'node_modules', '.git', '.pytest_cache'}]
                    for file in files:
                        if file.endswith(('.py', '.js', '.ts', '.vue')):
                            filepath = os.path.join(root, file)
                            file_imports = validate_stack.get_imports_from_file(filepath)
                            # ... rest of logic not strictly needed for walk performance
                return violations

            execution_time = timeit.timeit(run_validation, number=number)
            print(f"Validation walk ({number} iterations): {execution_time:.6f} seconds")

        finally:
            os.chdir(original_cwd)

if __name__ == "__main__":
    benchmark()
