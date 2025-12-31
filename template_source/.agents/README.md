# Agent System Template - Hidden Architecture

Welcome to the Agent System Template. This repository uses a "Clean Architecture" approach to keep AI configuration separate from your source code.

## 📂 The Hidden `.agents` Directory

All agent logic is contained within `.agents/`. You typically **do not** need to edit these files unless you are customizing the agents themselves.

*   `config/`: Defines who the agents are (Brain, Bolt, Sentinel, etc.).
*   `workflows/`: Defines how they behave (Standup, Code Review, etc.).
*   `rules/`: Defines global rules (e.g., "Don't debate small tasks").
*   `memory/`: Contains the project's history and roadmap. **Do not delete this** if you want the agents to remember context.

## 🛠️ Customizing the Agents

If you want to change how the agents behave (e.g., make Sentinel stricter), edit the files in `.agents/config/`.

If you want to change the "Standup" format, edit `.agents/workflows/standup.md`.

## 🧹 Cleaning Up

If you decide to stop using the System, you can simply delete the `.agents/` directory. Your `src/` code will remain untouched.
