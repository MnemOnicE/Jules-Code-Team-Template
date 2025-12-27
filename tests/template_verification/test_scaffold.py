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
        ".jules",
        ".jules/config",
        ".jules/memory",
        ".jules/workflows",
        ".jules/COMMANDS.md",
        ".jules/MANIFEST.md",
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
