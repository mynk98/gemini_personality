import sys
import os

path = 'architect/run_agent.py'
with open(path, 'r') as f:
    content = f.read()

# Fix the broken f-strings (removing the newline after f")
fixed = content.replace('f"
[Tool]', 'f"[Tool]')
fixed = fixed.replace('f"
--- Arch', 'f"--- Arch')
fixed = fixed.replace('f"User: {prompt}
"', 'f"User: {prompt}"')
fixed = fixed.replace('f"
Arch:', 'f"Arch:')

# Fix the Usage print string (missing escape for double quotes)
fixed = fixed.replace('python run_agent.py "<prompt>"', 'python run_agent.py "<prompt>"')

with open(path, 'w') as f:
    f.write(fixed)

print("Fixed architect/run_agent.py syntax.")
