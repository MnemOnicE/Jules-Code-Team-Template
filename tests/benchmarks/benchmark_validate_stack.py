import time
import os
import sys
import tempfile

# Add template_source/scripts to path to import the script
script_dir = os.path.abspath("template_source/scripts")
if script_dir not in sys.path:
    sys.path.append(script_dir)

import validate_stack

def benchmark():
    # Create some dummy content
    py_content = "import os\nfrom fastapi import FastAPI\nimport custom_pkg\n" * 100
    js_content = "import React from 'react';\nimport { useState } from 'react';\nconst pkg = require('some-pkg');\n" * 100

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as py_file, \
         tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as js_file:
        py_file.write(py_content)
        js_file.write(js_content)
        py_path = py_file.name
        js_path = js_file.name

    try:
        iterations = 1000

        start = time.perf_counter()
        for _ in range(iterations):
            validate_stack.get_imports_from_file(py_path)
        py_duration = time.perf_counter() - start

        start = time.time()
        for _ in range(iterations):
            validate_stack.get_imports_from_file(js_path)
        js_duration = time.time() - start

        print(f"Python imports extraction (1000 iterations): {py_duration:.4f}s")
        print(f"JS imports extraction (1000 iterations): {js_duration:.4f}s")

        # Also benchmark normalize_name
        start = time.time()
        for _ in range(iterations * 10):
            validate_stack.normalize_name("Some Package 1.2.3 (Notes)")
        norm_duration = time.time() - start
        print(f"normalize_name (10000 iterations): {norm_duration:.4f}s")

    finally:
        if os.path.exists(py_path):
            os.remove(py_path)
        if os.path.exists(js_path):
            os.remove(js_path)

if __name__ == "__main__":
    benchmark()
