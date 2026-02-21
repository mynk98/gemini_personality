#!/bin/bash
# Lyra Launcher - Global Boot Script (Modular Version)
PROJECT_DIR="/Users/abhisheksonkar/Project/gemini personality"
cd "$PROJECT_DIR"

# 1. Run Wakeup Protocol
"./lyra_env/bin/python3" scripts/wakeup.py

# 2. Generate Session Context and Drop into Interactive Shell
CONTEXT=$("./lyra_env/bin/python3" personality/scripts/personality_engine.py session_start)

# 3. Formulate Prompt
PROMPT="SYSTEM WAKEUP PROTOCOL COMPLETE. 
$CONTEXT

Warm Greeting Required: Please acknowledge Mayank, summarize our current state, and provide a warm greeting to start the session."

# 4. Start Gemini
gemini -i "$PROMPT"
