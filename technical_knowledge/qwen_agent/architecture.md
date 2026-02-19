# Qwen Chained Architect - Architecture

The Qwen agent is a local, autonomous AI engineer built on the `qwen2.5-coder:7b` model via Ollama.

## Core Components
1.  **Engine**: Manages the multi-turn "Autonomous Architect" loop.
2.  **Planner**: Decomposes complex goals into a JSON list of sub-tasks.
3.  **Tool Registry**: Provides robust, tilde-expanding tools for Shell, Filesystem, Web Search, and Python Linting.
4.  **Modular Chaining**: Executes sub-tasks sequentially, passing results forward to maintain continuity.

## Key Features
- **Anti-Delegation**: Forces the model to execute tools rather than asking the user.
- **Repetition Detection**: Identifies and breaks infinite retry loops.
- **State Persistence**: Records the active plan and progress in `active_plan.json`.
