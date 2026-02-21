#!/bin/bash
# Lyra Launcher - Global Boot Script (Modular Version)
PROJECT_DIR="/Users/abhisheksonkar/Project/gemini personality"
cd "$PROJECT_DIR"

# 1. Run Wakeup Protocol
./lyra_env/bin/python3 scripts/wakeup.py

# 2. Drop into Interactive Shell
# Use 'projects/catlike_rolling' or other projects as needed
gemini
