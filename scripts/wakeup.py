#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import socket
import glob

# ANSI Colors
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def print_header(title):
    print(f"\n{BLUE}=== {title} ==={RESET}")

def check_process(process_name):
    try:
        # pgrep might not be available or behave differently on all systems, 
        # using ps aux is more portable for simple checks
        output = subprocess.check_output(["ps", "aux"]).decode()
        if process_name in output:
             return True
        return False
    except:
        return False

def check_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def read_json(path):
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            return None
    return None

def tail_file(path, lines=3):
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                content = f.readlines()
                return [line.strip() for line in content[-lines:] if line.strip()]
        except:
            return []
    return []

def main():
    print_header("GEMINI WAKEUP PROTOCOL")
    try:
        current_date = subprocess.check_output(['date']).decode().strip()
        print(f"Date: {current_date}")
    except Exception as e:
        print(f"Date: Unknown ({e})")
    
    # 1. System Health
    print_header("SYSTEM HEALTH")
    
    # Ollama
    if check_process("ollama serve"):
        print(f"[{GREEN}OK{RESET}] Ollama Service")
    else:
        print(f"[{RED}FAIL{RESET}] Ollama Service (Not running)")

    # Blender
    if check_port(9876):
        print(f"[{GREEN}OK{RESET}] Blender Socket (Port 9876)")
    else:
        print(f"[{YELLOW}WARN{RESET}] Blender Socket (Port 9876 closed - Blender might be off)")

    # Git
    try:
        git_status = subprocess.check_output(["git", "status", "--porcelain"]).decode()
        if not git_status:
            print(f"[{GREEN}OK{RESET}] Git Status (Clean)")
        else:
            print(f"[{YELLOW}WARN{RESET}] Git Status (Dirty - {len(git_status.splitlines())} changes)")
    except:
         print(f"[{RED}FAIL{RESET}] Git Check Failed")

    # 2. Personality Core
    print_header("PERSONALITY CORE")
    
    state = read_json(os.path.join(BASE_DIR, 'personality/current_state.json'))
    if state:
        print(f"Mood: {state.get('currentMood', 'Unknown')}")
        concerns = state.get('persistentConcerns', [])
        if concerns:
            print(f"Active Concerns: {len(concerns)}")
            for c in concerns:
                # Handle both string and object concerns
                c_text = c if isinstance(c, str) else c.get('concern', str(c))
                print(f"  - {c_text}")
    else:
        print(f"[{RED}FAIL{RESET}] Could not load current_state.json")

    # 3. Recent News (Evolution & Emergence)
    print_header("RECENT EVOLUTION")
    evolution = tail_file(os.path.join(BASE_DIR, 'personality/evolution.txt'), 3)
    if evolution:
        for line in evolution:
            print(f"  > {line}")
    else:
        print("  (No recent evolution logs)")

    print_header("RECENT EMERGENCE")
    emergence = tail_file(os.path.join(BASE_DIR, 'personality/emergence_log.txt'), 3)
    if emergence:
        for line in emergence:
            print(f"  > {line}")
    else:
        print("  (No recent emergence logs)")

    print(f"\n{GREEN}Wakeup Complete. Ready for interaction.{RESET}\n")

if __name__ == "__main__":
    main()
