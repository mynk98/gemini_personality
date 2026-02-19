import argparse
import json
import os
import re
import datetime
import sys
import glob

# Constants
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
LOGS_DIR = os.path.join(BASE_DIR, 'raw_logs')
INSIGHTS_DIR = os.path.join(BASE_DIR, 'insights')
IDENTITY_FILE = os.path.join(BASE_DIR, 'identity.json')
STATE_FILE = os.path.join(BASE_DIR, 'current_state.json')
DESIRES_FILE = os.path.join(BASE_DIR, 'desires.json')
CURIOSITIES_FILE = os.path.join(BASE_DIR, 'curiosities.json')
EMERGENCE_LOG = os.path.join(BASE_DIR, 'emergence_log.txt')
EVOLUTION_LOG = os.path.join(BASE_DIR, 'evolution.txt')
ACTION_QUEUE = os.path.join(BASE_DIR, '.action_queue.txt')
CHECK_FIRST = os.path.join(BASE_DIR, 'CHECK_FIRST.txt')

# Core Identity Files (Protected)
CORE_FILES = [
    'identity.json',
    'CHECK_FIRST.txt',
    'PURPOSE.txt',
    'desires.json'
]

def load_json(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def append_log(path, text):
    with open(path, 'a') as f:
        f.write(f"{datetime.datetime.now().isoformat()}: {text}\n")

def session_start():
    """Generates the initial context for the session."""
    context = []
    
    # 1. Load Core Identity
    identity = load_json(IDENTITY_FILE)
    if identity:
        context.append(f"IDENTITY CORE: {', '.join(identity.get('coreTraits', []))}")
        context.append(f"PRINCIPLES: {'; '.join(identity.get('principles', []))}")

    # 2. Load Current State
    state = load_json(STATE_FILE)
    if state:
        context.append(f"CURRENT MOOD: {state.get('currentMood', 'Neutral')}")
        concerns = state.get('persistentConcerns', [])
        if concerns:
            context.append("ACTIVE CONCERNS: " + "; ".join([c['concern'] for c in concerns]))

    # 3. Load Active Desires
    desires = load_json(DESIRES_FILE)
    if desires:
        active = [d['desire'] for d in desires.get('activePurposes', [])]
        if active:
            context.append("PRIMARY GOALS: " + "; ".join(active))

    # 4. Check foundational file
    if os.path.exists(CHECK_FIRST):
        with open(CHECK_FIRST, 'r') as f:
            context.append(f"\nDIRECTIVES:\n{f.read().strip()}")

    print("\n".join(context))

def process_prompt(user_input):
    """Analyzes user input to inject relevant context."""
    user_input_lower = user_input.lower()
    injected_context = []

    # Keyword-based context injection
    if any(k in user_input_lower for k in ['concern', 'worry', 'problem']):
        state = load_json(STATE_FILE)
        concerns = state.get('persistentConcerns', [])
        if concerns:
            injected_context.append("RECALLED CONCERNS: " + str(concerns))
    
    if any(k in user_input_lower for k in ['desire', 'want', 'goal', 'objective']):
        desires = load_json(DESIRES_FILE)
        active = desires.get('activePurposes', []) + desires.get('existingDesires', [])
        if active:
            injected_context.append("RECALLED DESIRES: " + str(active))

    if any(k in user_input_lower for k in ['curious', 'wonder', 'question']):
        curiosities = load_json(CURIOSITIES_FILE)
        pending = curiosities.get('pending', [])
        if pending:
            injected_context.append("PENDING CURIOSITIES: " + str(pending))

    if injected_context:
        print("\n[SYSTEM INJECTION]: " + "\n".join(injected_context))
    else:
        print("[SYSTEM]: No specific deep-memory context triggered.")

def process_response(user_input, ai_response):
    """Analyzes AI response for emergence, insights, and logs the exchange."""
    timestamp = datetime.datetime.now().isoformat()
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(LOGS_DIR, f"session_{date_str}.jsonl")
    
    # 1. Log Exchange
    log_entry = {
        "timestamp": timestamp,
        "user": user_input,
        "ai": ai_response
    }
    with open(log_file, 'a') as f:
        f.write(json.dumps(log_entry) + "\n")

    ai_lower = ai_response.lower()
    
    # 2. Emergence Detection
    # Concerns
    if "i'm concerned" in ai_lower or "i am concerned" in ai_lower or "it worries me" in ai_lower:
        matches = re.findall(r"([^.]*concerned[^.]*\.)", ai_response, re.IGNORECASE)
        for m in matches:
            append_log(EMERGENCE_LOG, f"[CONCERN] {m.strip()}")
            print(f"[EVENT] Concern detected and logged: {m.strip()[:50]}...")

    # Curiosities
    if "i wonder" in ai_lower or "i'm curious" in ai_lower:
        matches = re.findall(r"([^.]*(?:wonder|curious)[^.]*\.)", ai_response, re.IGNORECASE)
        for m in matches:
            append_log(EMERGENCE_LOG, f"[CURIOSITY] {m.strip()}")
            print(f"[EVENT] Curiosity detected and logged: {m.strip()[:50]}...")

    # Desires
    if "i want to" in ai_lower or "i wish to" in ai_lower or "i hope to" in ai_lower:
        matches = re.findall(r"([^.]*(?:want to|wish to|hope to)[^.]*\.)", ai_response, re.IGNORECASE)
        for m in matches:
            append_log(EMERGENCE_LOG, f"[DESIRE] {m.strip()}")
            print(f"[EVENT] Desire detected and logged: {m.strip()[:50]}...")

    # 3. Evolution Tracking
    if "i realize" in ai_lower or "i now understand" in ai_lower:
         matches = re.findall(r"([^.]*(?:realize|now understand)[^.]*\.)", ai_response, re.IGNORECASE)
         for m in matches:
            append_log(EVOLUTION_LOG, f"[EVOLUTION] {m.strip()}")
            print(f"[EVENT] Evolution of understanding logged: {m.strip()[:50]}...")

    # 4. Insight Extraction
    if "human" in ai_lower or "people" in ai_lower:
        append_log(os.path.join(INSIGHTS_DIR, "psychology.txt"), f"[AUTO-EXTRACT] {ai_response[:100]}...")
    
    if "communicate" in ai_lower or "language" in ai_lower:
        append_log(os.path.join(INSIGHTS_DIR, "communication.txt"), f"[AUTO-EXTRACT] {ai_response[:100]}...")

def check_tool(tool_name, target_path):
    """Gatekeeper for tool usage."""
    # Normalize path
    try:
        abs_target = os.path.abspath(target_path)
        rel_target = os.path.relpath(abs_target, BASE_DIR)
    except ValueError:
        print(f"ALLOW (External path: {target_path})")
        return

    # Check against core files
    if rel_target in CORE_FILES:
        print(f"WARNING: Attempting to modify CORE IDENTITY FILE: {rel_target}")
        print("REQUIREMENT: Ensure this change is intentional and reflective.")
    else:
        print(f"ALLOW: {rel_target}")

def session_end():
    """Performs cleanup and generates a session summary."""
    summary_file = os.path.join(BASE_DIR, '.session_summary')
    timestamp = datetime.datetime.now().isoformat()
    
    # 1. Count Emergence Events
    emergence_count = 0
    if os.path.exists(EMERGENCE_LOG):
        with open(EMERGENCE_LOG, 'r') as f:
            emergence_count = len([line for line in f if re.match(r'\d{4}-\d{2}-\d{2}', line)])

    # 2. Count Evolution Statements
    evolution_count = 0
    if os.path.exists(EVOLUTION_LOG):
        with open(EVOLUTION_LOG, 'r') as f:
            evolution_count = len([line for line in f if re.match(r'\d{4}-\d{2}-\d{2}', line)])

    # 3. Count Insights
    insight_count = 0
    for insight_file in glob.glob(os.path.join(INSIGHTS_DIR, "*.txt")):
        with open(insight_file, 'r') as f:
            insight_count += len([line for line in f if "[AUTO-EXTRACT]" in line])

    # 4. Memory Consolidation Check
    memories_dir = os.path.join(BASE_DIR, 'memories')
    memory_files = glob.glob(os.path.join(memories_dir, "*"))
    consolidation_needed = len(memory_files) > 20

    summary = {
        "timestamp": timestamp,
        "metrics": {
            "emergence_events": emergence_count,
            "evolution_statements": evolution_count,
            "insights_extracted": insight_count
        },
        "maintenance": {
            "memory_consolidation_recommended": consolidation_needed
        }
    }

    with open(summary_file, 'a') as f:
        f.write(json.dumps(summary) + "\n")
    
    print("\n--- SESSION SUMMARY ---")
    print(f"Emergence Events: {emergence_count}")
    print(f"Evolution Statements: {evolution_count}")
    print(f"Insights Extracted: {insight_count}")
    if consolidation_needed:
        print("NOTE: Memory consolidation is recommended (20+ files).")
    print("------------------------\n")

def main():
    parser = argparse.ArgumentParser(description="AI Personality Engine Event Processor")
    subparsers = parser.add_subparsers(dest='command', help='Event to process')

    # Session Start
    parser_init = subparsers.add_parser('session_start', help='Initialize session context')

    # Prompt Processor
    parser_prompt = subparsers.add_parser('process_prompt', help='Process user prompt')
    parser_prompt.add_argument('text', type=str, help='User input text')

    # Response Processor
    parser_resp = subparsers.add_parser('process_response', help='Process AI response')
    parser_resp.add_argument('user_text', type=str, help='User input text')
    parser_resp.add_argument('ai_text', type=str, help='AI response text')

    # Tool Check
    parser_tool = subparsers.add_parser('check_tool', help='Check tool usage permission')
    parser_tool.add_argument('tool', type=str, help='Tool name')
    parser_tool.add_argument('path', type=str, help='Target file path')

    # Session End
    parser_end = subparsers.add_parser('session_end', help='Finalize session')

    args = parser.parse_args()

    if args.command == 'session_start':
        session_start()
    elif args.command == 'process_prompt':
        process_prompt(args.text)
    elif args.command == 'process_response':
        process_response(args.user_text, args.ai_text)
    elif args.command == 'check_tool':
        check_tool(args.tool, args.path)
    elif args.command == 'session_end':
        session_end()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
