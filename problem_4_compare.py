import json
import sys
import os

# Add current directory to path to import optimizer
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from optimizer import Sandbox


if __name__ == "__main__":
    # Get current directory path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(current_dir, "data.json")
    
    with open(data_path, "r") as f:
        data = json.load(f)
    


    with open("problem_4_claude4.5.py", "r") as f:
        claude_4_5 = f.read()
    with open("problem_4_grok4.1.py", "r") as f:
        grok_4_1 = f.read()
    with open("problem_4_ox.py", "r") as f:
        ox = f.read()
    
    test_cases = data[4]["test_cases"]
    

    sandbox = Sandbox()
    claude_4_5_result = sandbox.execute(claude_4_5, test_cases)
    grok_4_1_result = sandbox.execute(grok_4_1, test_cases)
    ox_result = sandbox.execute(ox, test_cases)
    print("OX: ", ox_result)
    print("Claude 4.5: ", claude_4_5_result)
    print("Grok 4.1: ", grok_4_1_result)
    
    
    with open("problem_4_results.json", "w") as f:
        json.dump({"claude_4_5": claude_4_5_result, "grok_4_1": grok_4_1_result, "ox": ox_result}, f)


