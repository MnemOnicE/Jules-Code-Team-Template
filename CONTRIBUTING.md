# Contributing to The Coding Squad Template

Welcome to the team! We are building the future of "Vibe Coding" with AI agents.

## 🧠 How to Contribute

1.  **Fork & Clone:** Fork the repo and clone it locally.
2.  **Initialize:** Run `python template_source/scripts/init_project.py` to set up the agent environment.
3.  **Branching:** Please use descriptive branch names (e.g., `feature/new-agent-persona` or `fix/init-script-bug`).

## 🤖 Working with Agents

If you are modifying the agent prompts in `.agents/config/`:
* **Verify Persona:** Ensure the voice matches the character (e.g., **Bolt** should be concise/mathematical, **Boom** should be energetic).
* **Test Constraints:** If you add a feature, ensure **Sentinel** or **Brain** has a rule to govern it.

## 🧪 Testing

* **Logic Checks:** Run `python template_source/scripts/smart_ingest.py` to ensure the memory system handles your changes.
* **Vibe Check:** Does the `init_project.py` script run without errors on a fresh install?

## 📜 Code of Conduct

Be excellent to each other. We optimize for flow, clarity, and kindness.
