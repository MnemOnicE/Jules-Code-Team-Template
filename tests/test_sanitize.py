
import sys
import os
import re

# Add the directory to sys.path to import from main
sys.path.insert(0, os.path.join(os.getcwd(), "template_source", ".agents", "engine"))

from main import _sanitize_llm_response

def test_sanitize_markdown_json():
    input_text = "```json\n{\"key\": \"value\"}\n```"
    expected = "{\"key\": \"value\"}"
    assert _sanitize_llm_response(input_text) == expected

def test_sanitize_markdown_raw():
    input_text = "```\n{\"key\": \"value\"}\n```"
    expected = "{\"key\": \"value\"}"
    assert _sanitize_llm_response(input_text) == expected

def test_sanitize_filler_heres_the_json():
    input_text = "Here's the JSON:\n{\"key\": \"value\"}"
    expected = "{\"key\": \"value\"}"
    assert _sanitize_llm_response(input_text) == expected

def test_sanitize_filler_result():
    input_text = "Result: {\"key\": \"value\"}"
    expected = "{\"key\": \"value\"}"
    assert _sanitize_llm_response(input_text) == expected

def test_sanitize_filler_output():
    input_text = "Output: {\"key\": \"value\"}"
    expected = "{\"key\": \"value\"}"
    assert _sanitize_llm_response(input_text) == expected

def test_sanitize_filler_graph():
    input_text = "Graph: {\"key\": \"value\"}"
    expected = "{\"key\": \"value\"}"
    assert _sanitize_llm_response(input_text) == expected

def test_sanitize_mixed_case():
    input_text = "here's the output: {\"foo\": \"bar\"}"
    expected = "{\"foo\": \"bar\"}"
    assert _sanitize_llm_response(input_text) == expected

def test_sanitize_no_filler():
    input_text = "{\"key\": \"value\"}"
    expected = "{\"key\": \"value\"}"
    assert _sanitize_llm_response(input_text) == expected

def test_sanitize_whitespace():
    input_text = "   \n  {\"key\": \"value\"}  \n  "
    expected = "{\"key\": \"value\"}"
    assert _sanitize_llm_response(input_text) == expected
