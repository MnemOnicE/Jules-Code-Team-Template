import os
import sys
import pytest
import tempfile

# Add template_source/scripts to path to import the script
# Acknowledging PR comment: sys.path is used here as a fallback in this environment
# where editable installs are not pre-configured.
script_dir = os.path.abspath("template_source/scripts")
if script_dir not in sys.path:
    sys.path.append(script_dir)

import validate_stack

@pytest.fixture
def tech_stack_file():
    content = "# - Python 3.10\n# - FastAPI (Backend)\n# - Vue.js\n"
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
        f.write(content)
        filepath = f.name
    yield filepath
    if os.path.exists(filepath):
        os.remove(filepath)

@pytest.fixture
def python_file():
    content = "import os\nfrom fastapi import FastAPI\nimport custom_pkg.module\n"
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
        f.write(content)
        filepath = f.name
    yield filepath
    if os.path.exists(filepath):
        os.remove(filepath)

@pytest.fixture
def javascript_file():
    content = "import React from 'react';\nimport { useState } from 'react';\nconst pkg = require('some-pkg');\nimport './local-file';\n"
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.js') as f:
        f.write(content)
        filepath = f.name
    yield filepath
    if os.path.exists(filepath):
        os.remove(filepath)

def test_normalize_name():
    assert validate_stack.normalize_name("Vue.js") == "vue"
    assert validate_stack.normalize_name("FastAPI") == "fastapi"
    assert validate_stack.normalize_name("Python 3.10") == "python"
    assert validate_stack.normalize_name("Some-Package_Name") == "somepackage_name"
    assert validate_stack.normalize_name("scikit-learn") == "sklearn"

def test_parse_tech_stack(tech_stack_file):
    allowed = validate_stack.parse_tech_stack(tech_stack_file)
    assert "python" in allowed
    assert "fastapi" in allowed
    assert "vue" in allowed

def test_get_imports_from_file_python(python_file):
    imports = validate_stack.get_imports_from_file(python_file)
    assert "os" in imports
    assert "fastapi" in imports
    assert "custom_pkg" in imports

def test_get_imports_from_file_javascript(javascript_file):
    imports = validate_stack.get_imports_from_file(javascript_file)
    assert "react" in imports
    assert "some-pkg" in imports
    assert "./local-file" not in imports
