import timeit
import sys
import os
import tempfile

# Add scripts directory to path
scripts_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "template_source", "scripts"))
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

from validate_stack import normalize_name, get_imports_from_file

def benchmark_normalize_name():
    names = [
        "FastAPI",
        "Python 3.10",
        "Vue.js",
        "scikit-learn",
        "SomePkg 2.0-beta",
        "my-package!",
        "  Strip Me  "
    ]

    def run():
        for name in names:
            normalize_name(name)

    number = 10000
    execution_time = timeit.timeit(run, number=number)
    print(f"normalize_name ({number} calls with {len(names)} names): {execution_time:.6f} seconds")
    print(f"Average time per call: {execution_time/(number * len(names)):.9f} seconds")

def benchmark_get_imports():
    py_content = """
import os
import sys
from collections import defaultdict
import numpy as np
from sklearn.linear_model import LogisticRegression
import my_local_module
"""
    js_content = """
import React from 'react';
import { useState, useEffect } from 'react';
import { Button } from '@mui/material';
import axios from 'axios';
import './style.css';
const config = require('./config.json');
const lodash = require('lodash');
"""

    with tempfile.NamedTemporaryFile(suffix=".py", mode='w', delete=False) as py_file:
        py_file.write(py_content)
        py_path = py_file.name

    with tempfile.NamedTemporaryFile(suffix=".js", mode='w', delete=False) as js_file:
        js_file.write(js_content)
        js_path = js_file.name

    try:
        def run():
            get_imports_from_file(py_path)
            get_imports_from_file(js_path)

        number = 5000
        execution_time = timeit.timeit(run, number=number)
        print(f"get_imports_from_file ({number} calls for py and js): {execution_time:.6f} seconds")
        print(f"Average time per file: {execution_time/(number * 2):.9f} seconds")
    finally:
        if os.path.exists(py_path):
            os.remove(py_path)
        if os.path.exists(js_path):
            os.remove(js_path)

if __name__ == "__main__":
    print("--- validate_stack Benchmark ---")
    benchmark_normalize_name()
    benchmark_get_imports()
