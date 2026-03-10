import os
import sys
import pytest
import tempfile

# Add template_source/scripts to path to import the script
sys.path.append(os.path.abspath("template_source/scripts"))
import validate_stack

def test_normalize_name():
    assert validate_stack.normalize_name("Vue.js") == "vue"
    assert validate_stack.normalize_name("FastAPI") == "fastapi"
    assert validate_stack.normalize_name("Python 3.10") == "python"
    assert validate_stack.normalize_name("Some-Package_Name") == "somepackage_name"
    assert validate_stack.normalize_name("scikit-learn") == "sklearn"

def test_parse_tech_stack():
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("# - Python 3.10\n")
        f.write("# - FastAPI (Backend)\n")
        f.write("# - Vue.js\n")
        temp_path = f.name

    try:
        allowed = validate_stack.parse_tech_stack(temp_path)
        assert "python" in allowed
        assert "fastapi" in allowed
        assert "vue" in allowed
    finally:
        os.remove(temp_path)

def test_get_imports_from_file_python():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("import os\n")
        f.write("from fastapi import FastAPI\n")
        f.write("import custom_pkg.module\n")
        temp_path = f.name

    try:
        imports = validate_stack.get_imports_from_file(temp_path)
        assert "os" in imports
        assert "fastapi" in imports
        assert "custom_pkg" in imports
    finally:
        os.remove(temp_path)

def test_get_imports_from_file_javascript():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write("import React from 'react';\n")
        f.write("import { useState } from 'react';\n")
        f.write("const pkg = require('some-pkg');\n")
        f.write("import './local-file';\n")
        temp_path = f.name

    try:
        imports = validate_stack.get_imports_from_file(temp_path)
        assert "react" in imports
        assert "some-pkg" in imports
        assert "./local-file" not in imports
    finally:
        os.remove(temp_path)
