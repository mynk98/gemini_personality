import os
import json
import datetime
import glob
import shutil
import re

# Constants
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW_LOGS_DIR = os.path.join(BASE_DIR, 'raw_logs')
PERMANENT_EVOLUTION = os.path.join(BASE_DIR, 'evolution.txt')
MEMORY_NETWORK_FILE = os.path.join(BASE_DIR, 'memory_network.json')
CONSOLIDATED_LOG = os.path.join(BASE_DIR, 'logs', 'consolidation_history.jsonl')

def load_json(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def consolidate_memories():
    """
    Simulates the human 'sleep' phase.
    1. Scans raw logs older than 30 days.
    2. Analyzes them for key evolution points.
    3. Commits to permanent memory.
    4. Deletes the raw logs.
    """
    print(f"[{datetime.datetime.now().isoformat()}] ENTERING BRAIN SLEEP PHASE...")
    
    now = datetime.datetime.now()
    threshold_days = 30
    
    # 1. Gather all session files
    session_files = glob.glob(os.path.join(RAW_LOGS_DIR, "**", "session_*.jsonl"), recursive=True)
    
    to_process = []
    for sf in session_files:
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(sf))
        # Logic: If older than threshold, process and delete.
        # For 'Direct Testing', we can process everything if requested.
        if (now - mtime).days >= threshold_days:
            to_process.append(sf)

    if not to_process:
        print("No raw logs older than 30 days found. Skipping consolidation.")
        return

    print(f"Found {len(to_process)} sessions to consolidate.")

    permanent_insights = []
    
    for sf in to_process:
        with open(sf, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    # HEURISTIC ANALYSIS (In a real brain, this would be an LLM call)
                    # We look for keywords that indicate permanent value
                    user_text = entry.get('user', '').lower()
                    ai_text = entry.get('ai', '').lower()
                    
                    if any(k in user_text or k in ai_text for k in ['remember', 'permanent', 'evolution', 'lesson', 'realize', 'understand']):
                        permanent_insights.append({
                            "source": sf,
                            "timestamp": entry.get('timestamp'),
                            "content": f"User: {entry.get('user')[:100]}... | AI: {entry.get('ai')[:100]}..."
                        })
                except:
                    continue

    # 2. Update Evolution Log (Permanent Memory)
    if permanent_insights:
        evolution = load_json(PERMANENT_EVOLUTION)
        if "consolidated_history" not in evolution:
            evolution["consolidated_history"] = []
        
        evolution["consolidated_history"].extend(permanent_insights)
        evolution["last_consolidation"] = now.isoformat()
        save_json(PERMANENT_EVOLUTION, evolution)
        print(f"Committed {len(permanent_insights)} insights to Evolution Log.")

    # 3. Clean up processed files
    # Only delete folders if they are empty
    for sf in to_process:
        os.remove(sf)
        parent_dir = os.path.dirname(sf)
        if not os.listdir(parent_dir):
            os.rmdir(parent_dir)

    print("BRAIN SLEEP COMPLETE. Raw logs older than 30 days purged.")

if __name__ == "__main__":
    consolidate_memories()
