import sys
import os
import pytest

# Add the scripts directory to sys.path to import the module
scripts_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "template_source", "scripts"))
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

from validate_stack import normalize_name, PACKAGE_MAPPING

def test_normalize_name_basic():
    """Test basic lowercasing and normalization."""
    assert normalize_name("FastAPI") == "fastapi"
    assert normalize_name("Python") == "python"

def test_normalize_name_mapping():
    """Test that items in PACKAGE_MAPPING are correctly handled."""
    # Based on PACKAGE_MAPPING = {"vue.js": "vue", "scikit-learn": "sklearn", "beautifulsoup4": "bs4", "pillow": "PIL"}
    assert normalize_name("Vue.js") == "vue"
    assert normalize_name("scikit-learn") == "sklearn"
    assert normalize_name("BeautifulSoup4") == "bs4"
    assert normalize_name("Pillow") == "PIL"

def test_normalize_name_version_stripping():
    """Test that version numbers are stripped from the name."""
    assert normalize_name("Python 3.10") == "python"
    assert normalize_name("Library 1.2.3") == "library"
    # Note: heuristic requires space before version
    assert normalize_name("SomePkg 2.0-beta") == "somepkg"
    # If no space, it won't strip (according to current regex \s+\d+)
    assert normalize_name("PackageV2") == "packagev2"

def test_normalize_name_special_chars():
    """Test removal of special characters except underscores."""
    assert normalize_name("my-package!") == "mypackage"
    assert normalize_name("complex.name@v1") == "complexnamev1"
    assert normalize_name("my_package") == "my_package"

def test_normalize_name_whitespace():
    """Test handling of whitespace."""
    # Input "  Strip Me  " -> lower "  strip me  " -> no version -> not in mapping
    # -> strip special chars (including spaces) -> "stripme"
    assert normalize_name("  Strip Me  ") == "stripme"
    assert normalize_name("Multiple   Spaces") == "multiplespaces"

def test_normalize_name_edge_cases():
    """Test various edge cases."""
    assert normalize_name("") == ""
    assert normalize_name("!!!") == ""
    assert normalize_name("123") == "123"
    assert normalize_name("already_normalized") == "already_normalized"


# --- Tests for PR changes: pre-compiled regex patterns and get_imports_from_file ---

import re
import sys
import os
import importlib

# Ensure validate_stack is importable
_scripts_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "template_source", "scripts"))
if _scripts_path not in sys.path:
    sys.path.insert(0, _scripts_path)


def test_precompiled_regex_patterns_exist():
    """PR added module-level pre-compiled regex constants — verify they exist and are compiled."""
    import validate_stack as vs
    assert hasattr(vs, 'VERSION_STRIP_RE'), "VERSION_STRIP_RE not found"
    assert hasattr(vs, 'NORMALIZE_RE'), "NORMALIZE_RE not found"
    assert hasattr(vs, 'NOTE_CLEANUP_RE'), "NOTE_CLEANUP_RE not found"
    assert hasattr(vs, 'PY_IMPORT_RE'), "PY_IMPORT_RE not found"
    assert hasattr(vs, 'JS_ES6_IMPORT_RE'), "JS_ES6_IMPORT_RE not found"
    assert hasattr(vs, 'JS_CJS_IMPORT_RE'), "JS_CJS_IMPORT_RE not found"

    # All should be compiled regex objects
    for attr in ('VERSION_STRIP_RE', 'NORMALIZE_RE', 'NOTE_CLEANUP_RE',
                 'PY_IMPORT_RE', 'JS_ES6_IMPORT_RE', 'JS_CJS_IMPORT_RE'):
        assert isinstance(getattr(vs, attr), type(re.compile(''))), \
            f"{attr} is not a compiled regex"


def test_py_import_re_matches_import_statements():
    """PY_IMPORT_RE should extract top-level package names from Python import statements."""
    import validate_stack as vs
    content = "import os\nimport sys\nfrom pathlib import Path\nfrom collections import OrderedDict\n"
    matches = vs.PY_IMPORT_RE.findall(content)
    assert "os" in matches
    assert "sys" in matches
    assert "pathlib" in matches
    assert "collections" in matches


def test_py_import_re_does_not_match_code_lines():
    """PY_IMPORT_RE should not match lines that aren't imports."""
    import validate_stack as vs
    content = "x = 5\nprint('hello')\nresult = some_func()\n"
    matches = vs.PY_IMPORT_RE.findall(content)
    assert matches == []


def test_js_es6_import_re_matches_es6_imports():
    """JS_ES6_IMPORT_RE should match ES6-style import statements."""
    import validate_stack as vs
    content = "import React from 'react';\nimport { useState } from 'react';\nimport express from 'express';\n"
    matches = vs.JS_ES6_IMPORT_RE.findall(content)
    assert "react" in matches
    assert "express" in matches


def test_js_es6_import_re_matches_scoped_packages():
    """JS_ES6_IMPORT_RE should match scoped packages like @org/pkg."""
    import validate_stack as vs
    content = "import something from '@scope/package';\n"
    matches = vs.JS_ES6_IMPORT_RE.findall(content)
    assert "@scope/package" in matches


def test_js_cjs_import_re_matches_require_calls():
    """JS_CJS_IMPORT_RE should match CommonJS require() calls."""
    import validate_stack as vs
    content = "const express = require('express');\nconst fs = require('fs');\n"
    matches = vs.JS_CJS_IMPORT_RE.findall(content)
    assert "express" in matches
    assert "fs" in matches


def test_note_cleanup_re_removes_parenthetical_notes():
    """NOTE_CLEANUP_RE should strip parenthetical notes like '(Backend)'."""
    import validate_stack as vs
    content = "FastAPI (Backend)"
    cleaned = vs.NOTE_CLEANUP_RE.sub('', content).strip()
    assert cleaned == "FastAPI"


def test_note_cleanup_re_handles_multiple_notes():
    """NOTE_CLEANUP_RE should remove multiple parenthetical notes."""
    import validate_stack as vs
    content = "Vue.js (Frontend) (v3)"
    cleaned = vs.NOTE_CLEANUP_RE.sub('', content).strip()
    assert "(Frontend)" not in cleaned
    assert "(v3)" not in cleaned


def test_get_imports_from_py_file(tmp_path):
    """get_imports_from_file should extract Python imports using PY_IMPORT_RE."""
    import validate_stack as vs
    py_file = tmp_path / "sample.py"
    py_file.write_text(
        "import os\nfrom pathlib import Path\nimport requests\nfrom collections import defaultdict\n",
        encoding='utf-8'
    )
    imports = vs.get_imports_from_file(str(py_file))
    assert "os" in imports
    assert "pathlib" in imports
    assert "requests" in imports
    assert "collections" in imports


def test_get_imports_from_js_file(tmp_path):
    """get_imports_from_file should extract JS ES6 and CJS imports."""
    import validate_stack as vs
    js_file = tmp_path / "sample.js"
    js_file.write_text(
        "import React from 'react';\nconst express = require('express');\n",
        encoding='utf-8'
    )
    imports = vs.get_imports_from_file(str(js_file))
    assert "react" in imports
    assert "express" in imports


def test_get_imports_from_js_file_filters_relative_imports(tmp_path):
    """get_imports_from_file should filter out relative imports starting with . or /."""
    import validate_stack as vs
    js_file = tmp_path / "sample.js"
    js_file.write_text(
        "import utils from './utils';\nimport helper from '../helper';\nimport lodash from 'lodash';\n",
        encoding='utf-8'
    )
    imports = vs.get_imports_from_file(str(js_file))
    assert "lodash" in imports
    assert not any(i.startswith('.') for i in imports)
    assert not any(i.startswith('/') for i in imports)


def test_parse_tech_stack_strips_parenthetical_notes(tmp_path):
    """parse_tech_stack should strip notes like '(Backend)' using NOTE_CLEANUP_RE."""
    import validate_stack as vs
    stack_file = tmp_path / "TECH_STACK.md"
    stack_file.write_text("# - FastAPI (Backend)\n# - Vue.js (Frontend)\n# - Requests\n")
    allowed = vs.parse_tech_stack(str(stack_file))
    # FastAPI (Backend) -> normalize FastAPI -> fastapi
    assert "fastapi" in allowed
    # Vue.js (Frontend) -> normalize vue.js -> vue (via PACKAGE_MAPPING)
    assert "vue" in allowed
    # Requests -> normalize -> requests
    assert "requests" in allowed


def test_parse_tech_stack_missing_file(tmp_path):
    """parse_tech_stack should return empty set when file does not exist."""
    import validate_stack as vs
    result = vs.parse_tech_stack(str(tmp_path / "nonexistent.md"))
    assert result == set()


def test_version_strip_re_strips_trailing_version(tmp_path):
    """VERSION_STRIP_RE should strip trailing version numbers with leading space."""
    import validate_stack as vs
    assert vs.VERSION_STRIP_RE.sub('', "Python 3.10") == "Python"
    assert vs.VERSION_STRIP_RE.sub('', "Library 1.2.3") == "Library"
    # No leading space before version means no stripping
    assert vs.VERSION_STRIP_RE.sub('', "PackageV2") == "PackageV2"
