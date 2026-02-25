# Jules Code Team Template
# Security Hardening Verification Tests

import os
import re

def test_oidc_security_fix():
    """
    Verify that the OIDC security fix is correctly applied to the Terraform configuration.
    It should use StringEquals, reference github_branch, and check the aud claim.
    """
    filepath = "template_source/infrastructure/identity/aws_oidc.tf"
    assert os.path.exists(filepath), f"{filepath} not found"

    with open(filepath, 'r') as f:
        content = f.read()

    # 1. Check for the presence of github_branch variable
    assert 'variable "github_branch"' in content, "github_branch variable not found in Terraform file"

    # 2. Check for the sub claim format (Strict branch-level filtering)
    # Expected: "token.actions.githubusercontent.com:sub" = "repo:${var.github_org}/${var.github_repo}:ref:refs/heads/${var.github_branch}"
    sub_claim_pattern = r'"token\.actions\.githubusercontent\.com:sub"\s*=\s*"repo:\${var\.github_org}/\${var\.github_repo}:ref:refs/heads/\${var\.github_branch}"'
    assert re.search(sub_claim_pattern, content), "Correct sub claim format not found (expected strict branch ref)"

    # 3. Ensure wildcard is removed
    assert ':*"' not in content, "Permissive wildcard ':*' still exists in the OIDC sub claim"

    # 4. Check for StringEquals (Exact match for better security)
    assert 'StringEquals =' in content, "StringEquals condition not found (should replace StringLike for exact matches)"

    # 5. Check for aud claim (Audience hardening)
    aud_claim_pattern = r'"token\.actions\.githubusercontent\.com:aud"\s*=\s*"sts\.amazonaws\.com"'
    assert re.search(aud_claim_pattern, content), "aud claim check not found (sts.amazonaws.com)"
