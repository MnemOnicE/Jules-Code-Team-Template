import os
import shutil
import tempfile
import time
import subprocess
import pytest

def test_scaffold_speed():
    """
    Benchmark the time it takes to scaffold the project.
    Goal: < 2 seconds.
    """
    start_time = time.time()

    with tempfile.TemporaryDirectory() as temp_dir:
        # Define source and destination
        source = os.path.abspath("template_source")
        destination = os.path.join(temp_dir, "new_project")

        # Copy the template
        shutil.copytree(source, destination)

        end_time = time.time()
        duration = end_time - start_time

        print(f"\nScaffold Duration: {duration:.4f} seconds")
        assert duration < 2.0, f"Scaffold took too long: {duration:.4f}s"

def test_data_generation_speed():
    """
    Benchmark the execution speed of the V3 data generation using the actual script.
    Goal: < 5 seconds.
    """
    # Create a temp env first (not timed)
    with tempfile.TemporaryDirectory() as temp_dir:
        source = os.path.abspath("template_source")
        destination = os.path.join(temp_dir, "new_project")
        shutil.copytree(source, destination)

        # Path to the actual script inside the scaffold
        # Now located at scripts/generate_v3_data.js inside the template
        script_path = os.path.join(destination, "scripts", "generate_v3_data.js")

        # Start timing
        start_time = time.time()

        result = subprocess.run(
            ["node", script_path],
            capture_output=True,
            text=True,
            cwd=destination
        )

        end_time = time.time()
        duration = end_time - start_time

        print(f"\nData Gen Duration: {duration:.4f} seconds")

        assert result.returncode == 0
        assert duration < 5.0, f"Data generation took too long: {duration:.4f}s"
