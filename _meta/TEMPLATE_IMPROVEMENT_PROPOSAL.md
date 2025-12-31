# Agent System Template Improvement Proposal

## 1. Problem Analysis

The current repository template suffers from **Meta-Bleed**, **Ambiguous Terminology**, and **Execution Bottlenecks**. The AI agents struggle to distinguish between their own operating instructions and the project they are building.

### A. Logic Bleeding (Contamination)
*   **Root Pollution:** Critical agent configuration files (`AGENTS.md`, `logs/`) reside in the project root. This confuses the LLM (e.g., "Does `AGENTS.md` describe *my* agents or the project's agents?").
*   **Scope Confusion:** The system instruction "The scope of `AGENTS.md` is the entire directory tree" causes rules intended for the *AI* (e.g., "Don't over-debate") to potentially be interpreted as rules for the *Project* (e.g., "Don't create debate threads in the app").
*   **Memory Leak:** `logs/` contains agent memories (`TEAM_MEMORY.md`) alongside potential project logs.

### B. Execution Reliability (Speed & Completion)
*   **The "Standup" Bottleneck:** The `STANDUP_PROTOCOL` attempts to do too much in one turn: Debate -> Decision -> Implementation -> Administration (3 file writes). This frequently hits token limits, causing the AI to skip the actual code implementation or the memory updates.
*   **Missing "Do It" Phase:** The protocol asks for an "Implementation Plan" but doesn't explicitly force a separate "Coding Phase".
*   **Overhead:** Updating 3 separate markdown files (`STANDUP_HISTORY`, `ROADMAP`, `TEAM_MEMORY`) for every single change is inefficient and prone to error.

### C. Terminology Conflict
*   **"Protocol":** The word is overloaded. If the user is building a network protocol, having `.agents/protocols` is confusing.
*   **Commands:** Commands like `/test` and `/standup` are generic.

---

## 2. Proposed "Clean Architecture" (v2)

We will restructure the repository to strictly separate **The Tool (Agents)** from **The Work (Project)**.

### Directory Structure
```text
.agents/                 <-- EVERYTHING Agent-related lives here
  ├── config/            <-- Static definitions (formerly definitions/)
  ├── workflows/         <-- Agent behaviors (formerly protocols/)
  ├── memory/            <-- Dynamic state (formerly logs/)
  │    ├── session.json  <-- Consolidated state (replaces multiple MD files)
  │    └── history.md    <-- Human-readable history
  ├── rules/             <-- Global rules (formerly AGENTS.md)
  └── manifest.json      <-- Central config file
src/                     <-- The User's Project (Clean)
README.md                <-- The User's Project README
```

### Key Changes

1.  **Consolidated Memory:** Instead of 3 separate files updated manually, we use a single `session.json` or `memory.md` inside `.agents/memory/`.
2.  **Renaming:**
    *   `protocols/` -> `workflows/` (Less generic).
    *   `AGENTS.md` -> `.agents/rules/WORKFLOW_RULES.md`.
    *   `logs/` -> `.agents/memory/`.
3.  **Explicit Phases:** We will split the "Standup" into two distinct turns/generations to ensure completion.
    *   **Phase 1:** The Meeting (Debate & Decision).
    *   **Phase 2:** The Work (Code Generation & Log Update).

---

## 3. Implementation Plan

### Step 1: Restructure (Isolation)
Move all root-level artifacts into `.agents/`. Update `SYSTEM_INSTRUCTIONS.md` to point to the new paths.

### Step 2: Refine Workflows
Rewrite `STANDUP_PROTOCOL.md` (now `workflows/standup.md`) to:
1.  Remove the "Step 6: Administration" from the *Debate* generation.
2.  Add a "Trigger" for the implementation phase.

### Step 3: Sanitize Terminology
Rename "Protocol" to "Workflow" in all docs.

### Step 4: "Fast Track" Rules
Update `WORKFLOW_RULES.md` to explicitly allow skipping the debate for tasks labeled "Small" or "Fix", defaulting to the `Implementation` phase immediately.

---

## 4. User Interaction Guide

A new file `.agents/README.md` will explain how to interact with the agents, ensuring the user knows where to find the "Hidden" logic if they need to customize it.
