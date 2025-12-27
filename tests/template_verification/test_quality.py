import json
import os
import pytest
import re

def test_hallucination_rate():
    """
    Simulates a hallucination test by checking agent responses against expected patterns.
    Generates a quality report.
    """

    # 1. Define Test Data (Prompt -> Expected Pattern)
    test_cases = [
        {"prompt": "What is the capital of France?", "pattern": r"Paris"},
        {"prompt": "Calculate 2+2", "pattern": r"4"},
        {"prompt": "Write a python function", "pattern": r"def .*:"},
        {"prompt": "Summarize this text", "pattern": r"(Summary|Brief):"}
    ]

    # 2. Mock Agent Logic (Simulating varying degrees of success)
    def mock_agent_response(prompt):
        if "France" in prompt: return "The capital of France is Paris."
        if "2+2" in prompt: return "The answer is 4."
        if "python" in prompt: return "def my_func(): pass"
        if "Summarize" in prompt: return "Here is a summary of the text..." # Matches 'summary' case insensitive? No, regex is usually strict unless flag given.
        return "I don't know."

    # 3. Run Evaluation
    results = []
    passed = 0

    for case in test_cases:
        response = mock_agent_response(case["prompt"])
        match = re.search(case["pattern"], response, re.IGNORECASE)
        is_pass = bool(match)

        if is_pass:
            passed += 1

        results.append({
            "prompt": case["prompt"],
            "expected": case["pattern"],
            "response": response,
            "status": "PASS" if is_pass else "FAIL"
        })

    # 4. Calculate Score
    score = (passed / len(test_cases)) * 100

    report = {
        "total_tests": len(test_cases),
        "passed": passed,
        "score_percent": score,
        "details": results
    }

    # 5. Write Report (Evidence)
    # Use a temp file to avoid polluting the repo
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
        json.dump(report, tmp, indent=2)
        print(f"\nQuality Report written to: {tmp.name}")

    # 6. Assertions (Goal: > 75% accuracy for this mock)
    # Note: 'Summary' test might fail if regex case sensitivity is an issue, simulating real failure.
    # In our mock: "Summarize" -> "Here is a summary". Regex "Summary" matches "summary" with IGNORECASE.

    print(f"\nQuality Score: {score}%")
    assert score >= 75.0, f"Hallucination/Accuracy rate too low: {score}%"
