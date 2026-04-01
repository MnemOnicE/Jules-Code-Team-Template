import sys
import os
import timeit
import tempfile

# Ensure we can import from template_source/scripts
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../template_source/scripts')))

from validate_stack import normalize_name, get_imports_from_file

def benchmark_normalize_name():
    names = [
        "Vue.js 3.0",
        "React 18.2.0",
        "FastAPI",
        "scikit-learn 1.2.0",
        "beautifulsoup4",
        "Pillow 9.5.0",
        "Express 4.18.2",
        "Next.js 13.4.1",
        "Mongoose 7.0.3",
        "PyTorch 2.0.1",
    ]

    def run():
        for name in names:
            normalize_name(name)

    times = timeit.repeat(run, number=10000, repeat=5)
    min_time = min(times)
    avg_time = sum(times)/len(times)
    print(f"normalize_name: min {min_time:.4f}s, avg {avg_time:.4f}s")
    return min_time

def benchmark_get_imports():
    py_content = """
import os
import sys
from collections import defaultdict
from foo.bar import baz
import xyzzy
"""
    js_content = """
import { something } from 'react';
import express from 'express';
const path = require('path');
const lodash = require('lodash');
"""

    fd_py, temp_py = tempfile.mkstemp(suffix='.py')
    fd_js, temp_js = tempfile.mkstemp(suffix='.js')

    try:
        with os.fdopen(fd_py, 'w') as f:
            f.write(py_content)
        with os.fdopen(fd_js, 'w') as f:
            f.write(js_content)

        def run():
            get_imports_from_file(temp_py)
            get_imports_from_file(temp_js)

        times = timeit.repeat(run, number=5000, repeat=5)
        min_time = min(times)
        avg_time = sum(times)/len(times)
        print(f"get_imports_from_file: min {min_time:.4f}s, avg {avg_time:.4f}s")
        return min_time
    finally:
        os.remove(temp_py)
        os.remove(temp_js)

if __name__ == "__main__":
    print("Benchmarking validate_stack.py")
    benchmark_normalize_name()
    benchmark_get_imports()
