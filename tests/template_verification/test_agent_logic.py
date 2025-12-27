import os
import pytest
import re

def test_workflow_rules_logic():
    """
    Test that WORKFLOW_RULES.md contains specific instructions for handling large files.
    """
    rules_path = "template_source/.jules/rules/WORKFLOW_RULES.md"
    assert os.path.exists(rules_path), "WORKFLOW_RULES.md not found"

    with open(rules_path, "r") as f:
        content = f.read()

    # Check for keywords related to large file handling
    # We are looking for something like "Large Payload" or "file size"
    # and instructions to use "summary" or "script".

    # Note: These exact phrases might not exist yet, which is the point of this test.
    # We want to enforce that they DO exist.

    # 1. Existence of the topic
    assert re.search(r"Large (Payload|File)", content, re.IGNORECASE), \
        "WORKFLOW_RULES.md does not mention 'Large Payload' or 'Large File' handling."

    # 2. Existence of the specific instruction (use summary/script)
    assert re.search(r"(summary|script|streaming)", content, re.IGNORECASE), \
        "WORKFLOW_RULES.md does not suggest using summary, script, or streaming for large files."

    # 3. Existence of the "Override" or "Flexible" clause (per user request)
    # The user wants "not hard and fast", so we look for "unless", "override", "deep dive", etc.
    assert re.search(r"(unless|override|deep dive|exception)", content, re.IGNORECASE), \
        "WORKFLOW_RULES.md does not include an exception/override clause for large file limits."

    # 4. Existence of the explicit 1MB limit definition
    # We want to ensure the rule is codified with a specific number.
    assert re.search(r"1\s?MB", content, re.IGNORECASE), \
        "WORKFLOW_RULES.md does not explicitly define the '1MB' limit."

def test_brain_awareness():
    """
    Test that brain.md references the rules or has similar awareness.
    """
    brain_path = "template_source/.jules/config/brain.md"
    assert os.path.exists(brain_path), "brain.md not found"

    with open(brain_path, "r") as f:
        content = f.read()

    # Brain should at least have some awareness of performance or stability limits.
    # The current brain.md has a "Decision Hierarchy" with "Performance (Bolt)".
    # That might be enough for now, but ideally it should reference the Workflow Rules.

    # For now, let's just check if it mentions "Performance" or "Stability".
    assert "Performance" in content or "Stability" in content, \
        "Brain agent does not seem to prioritize Performance or Stability."
