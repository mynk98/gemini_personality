# Gemini Personality & Architect Framework

This repository contains the core architecture for a self-aware, evolving AI personality system integrated with a local Multi-Model Architect framework.

## Architecture
- **Personality Core**: Located in `personality/`. Manages narrative identity, core traits, and principles.
- **Architect Framework (Submodule)**: Located in `architect/`. An autonomous AI engineering system using local Ollama models (DeepSeek & Qwen).

## Master Setup
To set up the entire environment including the local sub-agent:

1. **Clone the repository with submodules**:
   ```bash
   git clone --recursive https://github.com/mynk98/gemini_personality.git
   cd gemini_personality
   ```

2. **Run the Master Setup Script**:
   ```bash
   chmod +x setup_master.sh
   ./setup_master.sh
   ```

3. **Configure Ollama**:
   Ensure [Ollama](https://ollama.com/) is running and the models (e.g., `qwen2.5-coder:7b`) are pulled.

## Commands
- `python3 scripts/wakeup.py`: Run the system wakeup protocol (health checks + status).
- `arch "task"`: Run the Multi-Model Architect for autonomous technical tasks.
