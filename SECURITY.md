# Security Policy

## 🐺 The Sentinel Protocol & Philosophy

In the **Jules Code Team** architecture, security is an active participant, not just a static checklist. **Sentinel** (The Security Guardian) is designed to act as a hostile adversary within your development loop, enforcing "Zero Trust" and blocking vulnerable patterns before they merge.

However, we recognize that the *Orchestrator itself* (the Python scripts and Agent definitions) creates a new attack surface. We welcome security researchers to help us harden this framework.

## 📦 Supported Versions

We adhere to Semantic Versioning. Vulnerability reports are accepted only for the current major version.

| Version | Supported | Status |
| :--- | :--- | :--- |
| **v3.x** | ✅ Yes | **Active Agent System** |
| v2.x | ❌ No | Deprecated / End of Life |
| v1.x | ❌ No | Deprecated / End of Life |

## 🎯 Scope & Vulnerability Definition

Because this is an AI-powered tool, the definition of a "bug" can be fluid. Please use this guide to determine if you have found a reportable security vulnerability.

### ✅ In Scope (Report these!)
* **RCE in Tooling:** Remote Code Execution via `init_project.py` or `smart_ingest.py` (e.g., malicious filenames triggering execution).
* **Sentinel Bypass:** A repeatable prompt pattern that tricks **Sentinel** into approving code containing obvious OWASP Top 10 vulnerabilities (Injection, Hardcoded Secrets).
* **Context Leaks:** Exploits that force agents to read files outside the allowed project directory (Path Traversal).
* **Persistent Injection:** Prompt injection attacks that persist in `TEAM_MEMORY.md` and infect future sessions.

### ❌ Out of Scope (Do not report)
* **Generic Hallucinations:** Agents writing non-functional or buggy code (this is a quality issue, please open a GitHub Issue).
* **Behavioral "Jailbreaks":** Tricking an agent into being rude or breaking character, unless it leads to a Sentinel Bypass.
* **Social Engineering:** Attacks requiring you to convince a human developer to manually paste malicious commands.

## 🐞 Reporting a Vulnerability

**Please do not open public GitHub issues for security flaws.**

### 1. Private Disclosure
Email your report to: **[INSERT_YOUR_EMAIL_HERE]**
*(Optional: Encrypt your message using our PGP key: [LINK_TO_KEY])*

### 2. What to Include
* **Severity:** Critical (RCE/Secrets) vs. Moderate (Logic/Bypass).
* **The Vector:** Which agent failed? (e.g., "Boom overruled Sentinel").
* **Reproduction:** The specific prompt sequence or file structure required to trigger the exploit.

### 3. Our Response Timeline
* **Acknowledgment:** Within 48 hours.
* **Assessment:** Within 5 business days.
* **Fix/Patch:** Timeline determined by severity (Critical fixes prioritized < 24h).

## ⚓ Safe Harbor

We consider security research to be a vital activity. We will not pursue legal action against you for researching and reporting security vulnerabilities in this project, provided that you:

1.  Act in good faith to avoid privacy violations or destruction of data.
2.  Do not access or modify data residing in accounts you do not own.
3.  Give us reasonable time to remediate the issue before making it public.

## ⚔️ The "Deep Security" Standard

We assess findings based on our internal **Deep Security Audit** workflow:

* **Critical:** Exploits compromising the host machine (Developer Environment).
* **High:** Failures in **Sentinel's** core blocking logic (allowing confirmed CVE patterns).
* **Medium:** Weaknesses in `smart_ingest.py` token optimization or privacy filters.
* **Low:** Documentation errors or non-exploitable agent confusion.

## 📝 Attribution

We credit researchers who responsibly disclose vulnerabilities. Valid reports will be acknowledged in our Release Notes and strictly immortalized in our `TEAM_MEMORY.md`.
