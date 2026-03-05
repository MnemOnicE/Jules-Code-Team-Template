import time
import re
import os
import sys

# Add template_source/scripts to path to import the script
sys.path.append(os.path.abspath("template_source/scripts"))
import validate_stack

def benchmark():
    # Create some dummy content
    py_content = "import os\nfrom fastapi import FastAPI\nimport custom_pkg\n" * 100
    js_content = "import React from 'react';\nimport { useState } from 'react';\nconst pkg = require('some-pkg');\n" * 100

    # Mocking files is better, but for regex performance we can just call the functions if we refactor them slightly
    # or just use a temp file.

    with open("temp_bench.py", "w") as f:
        f.write(py_content)
    with open("temp_bench.js", "w") as f:
        f.write(js_content)

    iterations = 1000

    start = time.time()
    for _ in range(iterations):
        validate_stack.get_imports_from_file("temp_bench.py")
    py_duration = time.time() - start

    start = time.time()
    for _ in range(iterations):
        validate_stack.get_imports_from_file("temp_bench.js")
    js_duration = time.time() - start

    print(f"Python imports extraction (1000 iterations): {py_duration:.4f}s")
    print(f"JS imports extraction (1000 iterations): {js_duration:.4f}s")

    # Also benchmark normalize_name
    start = time.time()
    for _ in range(iterations * 10):
        validate_stack.normalize_name("Some Package 1.2.3 (Notes)")
    norm_duration = time.time() - start
    print(f"normalize_name (10000 iterations): {norm_duration:.4f}s")

    os.remove("temp_bench.py")
    os.remove("temp_bench.js")

if __name__ == "__main__":
    benchmark()
