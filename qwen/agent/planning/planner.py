import ollama
import json

class Planner:
    def __init__(self, model_name="qwen2.5-coder:7b"):
        self.model = model_name

    def decompose(self, goal):
        prompt = f"""Break down the following complex AI engineering goal into a sequence of small, verifiable sub-tasks. 
        Each sub-task must be independent enough to be solved in a few tool calls.
        
        GOAL: {goal}
        
        Output your response strictly as a JSON list of strings.
        Example: ["Create directory X", "Write script Y", "Run and verify Z"]
        """
        
        print("[Planner] Decomposing goal into sub-tasks...")
        response = ollama.chat(
            model=self.model,
            messages=[{'role': 'user', 'content': prompt}]
        )
        
        content = response['message']['content']
        try:
            # Try to extract JSON list
            if "[" in content and "]" in content:
                json_str = content[content.find("["):content.rfind("]")+1]
                return json.loads(json_str)
        except:
            pass
            
        # Fallback: simple line-based split if JSON fails
        return [line.strip() for line in content.split('\n') if line.strip() and (line[0].isdigit() or line.startswith('-'))]
