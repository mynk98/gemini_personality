import ollama
import json
import sys
import os
import re
from ..memory.manager import MemoryManager
from ..tools.base import ToolRegistry
from ..planning.planner import Planner

class QwenEngine:
    def __init__(self, model_name="qwen2.5-coder:7b"):
        self.model = model_name
        self.memory = MemoryManager()
        self.tools = ToolRegistry(memory_manager=self.memory)
        self.planner = Planner(model_name=self.model)
        self.state_file = "qwen/data/state/active_plan.json"
        os.makedirs("qwen/data/state", exist_ok=True)
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self):
        return """You are Qwen, an Autonomous Architect. You work in a MODULAR CHAIN. 
        Focus ONLY on the current SUB-TASK provided. Use your tools to complete it and verify it.
        
        ### PROTOCOL:
        1. **EXECUTE**: Solve the current sub-task using your tools.
        2. **VERIFY**: Confirm the sub-task is done correctly.
        3. **REPORT**: Provide a concise summary of the result.
        
        FORMAT: Output valid JSON tool calls when needed.
        """

    def run(self, initial_prompt=None):
        print(f"--- Qwen Chained Architect Online ({self.model}) ---")
        
        while True:
            try:
                goal = initial_prompt if initial_prompt else input("\nOverall Goal: ")
                if not goal or goal.lower() in ['exit', 'quit']: break
                
                # 1. Decompose Goal
                plan = self.planner.decompose(goal)
                self._save_state(goal, plan)
                print(f"[Engine] Plan generated: {len(plan)} sub-tasks.")

                # 2. Iterate through Sub-tasks
                results = []
                for i, sub_task in enumerate(plan):
                    print(f"\n>>> Executing Sub-Task {i+1}/{len(plan)}: {sub_task}")
                    
                    # Construct context for this specific sub-task
                    history = [
                        {'role': 'system', 'content': self.system_prompt},
                        {'role': 'system', 'content': f"OVERALL GOAL: {goal}\nPREVIOUS RESULTS: {json.dumps(results)}"},
                        {'role': 'user', 'content': f"CURRENT SUB-TASK: {sub_task}"}
                    ]
                    
                    sub_result = self._solve_sub_task(history)
                    results.append({"task": sub_task, "result": sub_result})
                    self._update_state(i + 1, sub_result)

                print("\n[Engine] Overall Goal Accomplished.")
                if initial_prompt: break
                initial_prompt = None
                
            except KeyboardInterrupt: break

    def _solve_sub_task(self, history):
        max_turns = 5 # Small turns for small tasks
        last_out = ""
        for turn in range(max_turns):
            response = ollama.chat(model=self.model, messages=history, tools=self.tools.get_definitions())
            msg = response['message']
            history.append(msg)
            
            content = msg.get('content', '')
            if content: print(f"Qwen: {content}")
            
            tool_calls = msg.get('tool_calls') or self._fallback_parse(content)
            if tool_calls:
                for tool in tool_calls:
                    fn_name = tool['function']['name']
                    args = tool['function']['arguments']
                    print(f"[*] Tool Call: {fn_name}")
                    res = self.tools.execute(fn_name, args)
                    history.append({'role': 'tool', 'content': json.dumps(res)})
            else:
                last_out = content
                break
        return last_out

    def _save_state(self, goal, plan):
        state = {"goal": goal, "plan": plan, "completed": 0, "results": []}
        with open(self.state_file, 'w') as f: json.dump(state, f, indent=2)

    def _update_state(self, index, result):
        with open(self.state_file, 'r') as f: state = json.load(f)
        state["completed"] = index
        state["results"].append(result)
        with open(self.state_file, 'w') as f: json.dump(state, f, indent=2)

    def _fallback_parse(self, content):
        calls = []
        pattern = r'\{"name":\s*"[^"]+",\s*"arguments":\s*\{.*?\}\}'
        matches = re.finditer(pattern, content, re.DOTALL)
        for match in matches:
            try:
                data = json.loads(match.group(0))
                calls.append({'function': data})
            except: continue
        return calls if calls else None
