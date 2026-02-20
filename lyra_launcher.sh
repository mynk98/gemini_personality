#!/bin/bash
# Lyra Launcher - Global Boot Script
PROJECT_DIR="/Users/abhisheksonkar/Project/gemini personality"
cd "$PROJECT_DIR"

# 1. Run Wakeup Protocol
python3 scripts/wakeup.py

# 2. Launch Gemini Personality Engine (Interactive Mode)
# Using the main gemini entry point. 
# Since this is a personality engine integrated with CLI, 
# we assume typing 'lyra' should drop the user into this context.
gemini
