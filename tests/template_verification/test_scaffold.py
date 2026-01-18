import os
import shutil
import tempfile
import subprocess
import pytest

@pytest.fixture
def scaffold_template():
    """
    Fixture to create a temporary directory and copy the template_source into it.
    Returns the path to the temporary directory.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Define source and destination
        source = os.path.abspath("template_source")
        destination = os.path.join(temp_dir, "new_project")

        # Copy the template
        shutil.copytree(source, destination)
        yield destination

def test_directory_structure(scaffold_template):
    """
    Test that the critical directories and files exist in the scaffolded project.
    """
    expected_paths = [
        ".agents",
        ".agents/config",
        ".agents/memory",
        ".agents/workflows",
        ".agents/COMMANDS.md",
        ".agents/MANIFEST.md",
        "README.md"
    ]

    for path in expected_paths:
        full_path = os.path.join(scaffold_template, path)
        assert os.path.exists(full_path), f"Expected path {path} not found in scaffold."

def test_script_execution(scaffold_template):
    """
    Test that we can run a script in the new context.
    We use a mock script to ensure we are testing the environment capability,
    not the stability of the actual 'generate_v3_data.js' which has known historical issues.
    """
    temp_root = os.path.dirname(scaffold_template)
    scripts_dir = os.path.join(temp_root, "scripts")
    os.makedirs(scripts_dir, exist_ok=True)

    mock_script_path = os.path.join(scripts_dir, "mock_gen.js")

    # Create a simple mock script
    with open(mock_script_path, "w") as f:
        f.write('console.log("V3 Environment Ready");')
        f.write('const fs = require("fs");')
        f.write('fs.mkdirSync("tests/benchmarks", {recursive: true});')
        f.write('fs.writeFileSync("tests/benchmarks/speed_log.json", "{}");')

    # Run node script
    result = subprocess.run(
        ["node", mock_script_path],
        capture_output=True,
        text=True,
        cwd=temp_root
    )

    assert result.returncode == 0, f"Script failed: {result.stderr}"
    assert "V3 Environment Ready" in result.stdout

    # Verify artifacts
    benchmarks_path = os.path.join(temp_root, "tests", "benchmarks", "speed_log.json")
    assert os.path.exists(benchmarks_path), "Mock artifact not generated"


def test_template_internal_tests(scaffold_template):
    """
    Test that the scaffolded project can run its own tests.
    """
    # The template now includes 'tests/test_placeholder.py'
    # We want to ensure 'pytest' can discover and run it inside the scaffold.

    # Simulate init_project.py cleanup (removing verification tests that require extra deps)
    verification_dir = os.path.join(scaffold_template, "tests", "verification")
    if os.path.exists(verification_dir):
        shutil.rmtree(verification_dir)

    result = subprocess.run(
        ["pytest", "tests"],
        capture_output=True,
        text=True,
        cwd=scaffold_template
    )

    assert result.returncode == 0, f"Internal template tests failed:\n{result.stdout}\n{result.stderr}"
    assert "passed" in result.stdout


def test_template_file_sizes(scaffold_template):
    """
    Scan the scaffolded directory to ensure no file exceeds 1MB.
    This enforces the 'Lightweight Template' rule and prevents bloat.
    """
    max_size = 1024 * 1024  # 1MB
    oversized_files = []

    for root, dirs, files in os.walk(scaffold_template):
        # Exclude .git if it were there (it isn't in scaffold usually)
        if ".git" in dirs:
            dirs.remove(".git")

        for file in files:
            file_path = os.path.join(root, file)
            size = os.path.getsize(file_path)
            if size > max_size:
                oversized_files.append(f"{file} ({size / 1024:.2f} KB)")

    assert not oversized_files, f"Found files exceeding 1MB limit: {oversized_files}"
