# Jules Template - Hidden Architecture

Welcome to the Jules Agent Template. This repository uses a "Clean Architecture" approach to keep AI configuration separate from your source code.

## 📂 The Hidden `.jules` Directory

All agent logic is contained within `.jules/`. You typically **do not** need to edit these files unless you are customizing the agents themselves.

*   `config/`: Defines who the agents are (Brain, Bolt, Sentinel, etc.).
*   `workflows/`: Defines how they behave (Standup, Code Review, etc.).
*   `rules/`: Defines global rules (e.g., "Don't debate small tasks").
*   `memory/`: Contains the project's history and roadmap. **Do not delete this** if you want the agents to remember context.

## 🛠️ Customizing the Agents

If you want to change how the agents behave (e.g., make Sentinel stricter), edit the files in `.jules/config/`.

If you want to change the "Standup" format, edit `.jules/workflows/standup.md`.

## 🧹 Cleaning Up

If you decide to stop using Jules, you can simply delete the `.jules/` directory. Your `src/` code will remain untouched.
