"""
Code Optimizer with LLM - Simplified Version
"""

import json
import time
import random
import math
import ast
from typing import Dict, List, Tuple

from api import chat_completion
from visualizer import OptimizerVisualizer
from backup_manager import BackupManager
# ============================================================================
# Default Settings
# ============================================================================
PLANNING_MODELS = [
    "gemini-2.5-pro",
    "gemini-2.5-pro-preview-03-25",
    "gemini-2.5-pro-preview-05-06",
    "gemini-2.5-pro-preview-06-05",
    "gemini-pro-latest",
    "deepseek-v3.1:671b-cloud",      # 671B parameters - reasoning giant
   
          # 480B - specialized for code but also good for planning
    "gpt-oss:120b-cloud", 
              # GLM-4 - balanced and fast

]






"""
Improved Prompt Builder - with Context and Strategy
"""

def build_improved_prompt(
    code: str,
    test_cases: List[Dict],
    current_metrics: Dict,
    iteration: int,
    history: List[Dict] = None,
    strategy: str = None
) -> str:
    """
    Build advanced prompt with:
    - Context from history
    - Specific strategy
    - Better examples
    - Clearer format
    """
    
    # ========== Test Cases ==========
    tests_str = "\n".join([
        f"  • {t['function']}({_format_input(t['input'])}) → {t['expected']}"
        for i, t in enumerate(test_cases)
    ])
    
    # ========== Current Metrics ==========
    exec_time = current_metrics.get('execution_time', float('inf'))
    mem_usage = current_metrics.get('memory_usage', float('inf'))
    tests_passed = current_metrics.get('tests_passed', 0)
    tests_failed = current_metrics.get('tests_failed', 0)
    total_tests = tests_passed + tests_failed
    
    metrics_str = f"""
  • Execution Time: {_format_time(exec_time)}
  • Memory Usage: {_format_memory(mem_usage)}
  • Tests Passed: {tests_passed}/{total_tests}
  • Test Success Rate: {(tests_passed/total_tests*100):.1f}%"""
    
    if current_metrics.get('errors') and len(current_metrics.get('errors', [])) > 0:
        metrics_str += f"\n  • Errors: {current_metrics['errors'][0][:100]}..."
    
    # ========== History Context (Treasure!) ==========
    history_context = ""
    if history and len(history) > 1:
        # 3 best
        successful = [h for h in history[1:] if h.get('accepted') and h['metrics'].get('tests_failed', 999) == 0]
        if successful:
            best_3 = sorted(successful, key=lambda x: x['energy'])[:3]
            history_context += "\n**Previously Successful Optimizations:**\n"
            for h in best_3:
                improvement = ((history[0]['energy'] - h['energy']) / history[0]['energy'] * 100)
                history_context += f"  ✅ Iteration {h['iteration']}: {improvement:.1f}% improvement\n"
        
        # 2 failed
        failed = [h for h in history[1:] if not h.get('accepted') or h['metrics'].get('tests_failed', 0) > 0]
        if failed:
            worst_2 = failed[-2:]  # latest failures
            history_context += "\n**Recently Failed Attempts:**\n"
            for h in worst_2:
                errors = h['metrics'].get('errors', [])
                if errors and len(errors) > 0:
                    error_msg = errors[0][:80]
                else:
                    error_msg = 'Unknown error'
                history_context += f"  ❌ Iteration {h['iteration']}: {error_msg}\n"
    
    # ========== Strategy-Specific Guidance ==========
    strategy_guide = _get_strategy_guide(strategy, code)
    
    # ========== Examples (Few-Shot Learning) ==========
    examples = """
**Example 1 - List Comprehension:**
Before:
```python
result = []
for x in data:
    if x > 0:
        result.append(x * 2)
```
After:
```python
result = [x * 2 for x in data if x > 0]
```

**Example 2 - Early Exit:**
Before:
```python
for item in big_list:
    if condition(item):
        found = item
```
After:
```python
found = next((item for item in big_list if condition(item)), None)
```

**Example 3 - Set Lookup (O(1) vs O(n)):**
Before:
```python
if x in my_list:  # O(n)
```
After:
```python
my_set = set(my_list)
if x in my_set:  # O(1)
```
"""
    
    # ========== Main Prompt ==========
    prompt = f"""You are an expert Python performance optimizer with deep knowledge of algorithms, data structures, and Python internals.

{'='*70}
CURRENT CODE (Iteration {iteration})
{'='*70}
```python
{code}
```

{'='*70}
TEST CASES (ALL MUST PASS - Correctness is CRITICAL)
{'='*70}
{tests_str}

{'='*70}
CURRENT PERFORMANCE METRICS
{'='*70}
{metrics_str}

{history_context}

{'='*70}
YOUR OPTIMIZATION TASK
{'='*70}
{strategy_guide}

**Critical Requirements:**
1. ✅ **MUST pass ALL test cases** - Correctness > Speed
2. 🚀 **Improve execution time or memory usage**
3. 📖 **Keep code readable and maintainable**
4. 🔍 **Focus on algorithmic improvements, not micro-optimizations**

**Optimization Techniques to Consider:**
• Algorithmic complexity reduction (O(n²) → O(n log n) or O(n))
• Better data structures (list → set/dict for lookups)
• List comprehensions and generator expressions
• Early exit conditions (break/return when possible)
• Avoid repeated calculations (cache/memoize)
• Vectorization with built-in functions (sum, map, filter)
• Remove unnecessary loops or nested iterations

{examples}

{'='*70}
RESPONSE FORMAT (STRICT JSON - No markdown, no explanations outside JSON)
{'='*70}
{{
  "analysis": "Brief analysis of current bottleneck (1-2 sentences)",
  "strategy": "Which optimization technique you're applying",
  "code": "Complete optimized code (must be valid Python, fully functional)",
  "reasoning": "Why this should be faster/more efficient (technical explanation)",
  "estimated_improvement": "Expected percentage improvement (e.g., '20-30%')"
}}

**IMPORTANT:** 
- Return ONLY valid JSON
- The "code" field must contain complete, runnable Python code
- Do NOT use markdown code blocks (```) in the JSON
- Ensure all test cases will pass with your code"""

    return prompt


def _format_input(inp):
    """Format input for better readability"""
    if isinstance(inp, dict):
        return ", ".join(f"{k}={v}" for k, v in inp.items())
    elif isinstance(inp, list):
        if len(inp) == 1:
            return str(inp[0])
        return str(inp)
    return str(inp)


def _format_time(t: float) -> str:
    """Format time with appropriate unit"""
    if t == float('inf'):
        return "TIMEOUT"
    elif t < 0.0001:
        return f"{t*1000000:.2f}μs"
    elif t < 0.001:
        return f"{t*1000:.3f}ms"
    elif t < 1:
        return f"{t*1000:.2f}ms"
    else:
        return f"{t:.4f}s"


def _format_memory(m: float) -> str:
    """Format memory with appropriate unit"""
    if m == float('inf'):
        return "OUT OF MEMORY"
    elif m < 0.001:
        return f"{m*1024:.2f}KB"
    elif m < 1:
        return f"{m:.3f}MB"
    else:
        return f"{m:.2f}MB"


def _get_strategy_guide(strategy: str, code: str) -> str:
    """Strategy-specific guide"""
    
    strategies = {
        "algorithmic": """
**Focus: Algorithmic Complexity Reduction**
- Look for nested loops → can they be reduced?
- Is there a better algorithm? (sorting, binary search, etc.)
- Can you use hash tables for O(1) lookups?
Target: Reduce Big-O complexity""",
        
        "data_structures": """
**Focus: Data Structure Optimization**
- Are you doing `if x in list`? → Use set/dict
- Multiple list lookups? → Pre-convert to set
- Need ordering + fast lookup? → Use OrderedDict
Target: O(n) → O(1) operations""",
        
        "comprehensions": """
**Focus: Pythonic Code & Comprehensions**
- Replace explicit loops with list/dict comprehensions
- Use generator expressions for memory efficiency
- Apply map/filter where appropriate
Target: More concise, faster code""",
        
        "caching": """
**Focus: Avoid Redundant Computation**
- Are you recalculating the same values?
- Can you store intermediate results?
- Use memoization for recursive functions
Target: Eliminate duplicate work""",
        
        "early_exit": """
**Focus: Early Exit & Short-Circuit**
- Can you return/break earlier?
- Use `any()` or `all()` for boolean checks
- Add guard clauses at function start
Target: Process less data""",
        
        "vectorization": """
**Focus: Built-in Functions & Operations**
- Use sum(), min(), max() instead of loops
- Apply built-in string methods
- Leverage stdlib functions (itertools, functools)
Target: Native C-speed operations"""
    }
    
    if strategy and strategy in strategies:
        return strategies[strategy]
    
    # Default: general guide
    return """
**Focus: General Performance Optimization**
Analyze the code and apply the MOST IMPACTFUL optimization.
Consider: algorithms, data structures, unnecessary work, bottlenecks."""


# ========== Strategy Selector ==========
def select_strategy(iteration: int, max_iterations: int, code: str, history: List[Dict]) -> str:
    """
    Intelligent strategy selection based on:
    - Iteration number
    - Code characteristics  
    - History of what worked
    """
    
    strategies = [
        "algorithmic",
        "data_structures", 
        "comprehensions",
        "caching",
        "early_exit",
        "vectorization"
    ]
    
    # First: algorithmic (most impact)
    if iteration <= max_iterations * 0.3:
        return "algorithmic"
    
    # Middle: data structures
    elif iteration <= max_iterations * 0.5:
        return "data_structures"
    
    # Then: other strategies in rotation
    else:
        idx = iteration % len(strategies)
        return strategies[idx]


# ========== Usage Example ==========


























from google import genai
import threading
import os

def parse_json_response(response_text: str) -> Tuple[Dict, str]:
    """Parse JSON response from LLM, handling markdown code blocks"""
    try:
        # Clean the response
        text = response_text.strip()
        
        # Remove markdown code blocks if present
        if text.startswith("```"):
            parts = text.split("```")
            if len(parts) >= 3:
                # Find the JSON part
                for part in parts:
                    part = part.strip()
                    if part.startswith("json"):
                        part = part[4:].strip()
                    if part.startswith("{") or part.startswith("["):
                        text = part
                        break
        
        # Try to find JSON object in the text
        start_idx = text.find("{")
        if start_idx != -1:
            # Find matching closing brace
            brace_count = 0
            end_idx = start_idx
            for i in range(start_idx, len(text)):
                if text[i] == "{":
                    brace_count += 1
                elif text[i] == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        end_idx = i + 1
                        break
            
            if end_idx > start_idx:
                json_str = text[start_idx:end_idx]
                parsed = json.loads(json_str)
                return parsed, None
        
        # Try parsing the whole text
        parsed = json.loads(text)
        return parsed, None
        
    except json.JSONDecodeError as e:
        return None, f"JSON parsing error: {str(e)}"
    except Exception as e:
        return None, f"Error parsing response: {str(e)}"


def call_google_model(model_name: str, prompt: str, api_key: str, timeout: int = 60, parse_func=None):
    """Call Google Gemini model with timeout"""
    import threading
    

    
    # Log which API key is being used (last 8 chars for security)
    api_key_suffix = api_key[-8:] if len(api_key) > 8 else "***"
    print(f"🔑 Using API key: ...{api_key_suffix} for {model_name}")
    
    client = genai.Client(api_key=api_key)
    result_container = {"response": None, "error": None, "done": False}
    
    def api_call():
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            result_container["response"] = response
        except Exception as e:
            result_container["error"] = str(e)
        finally:
            result_container["done"] = True
    
    # Start API call in a thread
    thread = threading.Thread(target=api_call, daemon=True)
    thread.start()
    thread.join(timeout=timeout)
    
    if not result_container["done"]:
        return {
            "model": model_name,
            "output": "",
            "success": False,
            "error": f"Google API call timeout after {timeout}s"
        }
    
    if result_container["error"]:
        return {
            "model": model_name,
            "output": "",
            "success": False,
            "error": result_container["error"]
        }
    
    try:
        parsed_output, error = parse_func(result_container["response"].text)
        if parsed_output is None:
            return {
                "model": model_name,
                "output": result_container["response"].text,
                "success": False,
                "error": error
            }

        return {
            "model": model_name,
            "output": parsed_output,
            "success": True,
            "error": None
        }
    except Exception as e:
        return {
            "model": model_name,
            "output": "",
            "success": False,
            "error": str(e)
        }


def call_ollama_model(model: str, prompt: str, api_key: str, parse_func=None):
    """Call Ollama model"""
    if parse_func is None:
        parse_func = parse_json_response
    
    try:
        output = chat_completion(model=model, prompt=prompt, api_key=api_key)
        parsed_output, error = parse_func(output)
        if parsed_output is None:
            return {
                "model": model,
                "output": output,
                "success": False,
                "error": error
            }

        return {
            "model": model,
            "output": parsed_output,
            "success": True,
            "error": None
        }
    except Exception as e:
        return {
            "model": model,
            "output": "",
            "success": False,
            "error": str(e)
        }

DEFAULT_CONFIG = {
    "max_iterations": 20,
    "num_variants": 3,
    "model": "deepseek-v3.1:671b-cloud",  # Default to a model from PLANNING_MODELS
    "temperature": 0.7,
    "weights": {"speedup": 1.0, "correctness": 10.0, "complexity": 0.5, "memory_usage": 0.5},
    "cooling": {"initial_temp": 100.0, "final_temp": 0.1},
    "verbose": True
}

api_key_list=[
"REDACTED_API_KEY",
"REDACTED_API_KEY",
"REDACTED_API_KEY",
]
# ============================================================================
# LLM Interface
# ============================================================================

def call_llm(prompt: str, model: str, temp: float = 0.7, api_key: str = None) -> str:
    """Call LLM API based on model type"""
    if api_key is None:
        # Try to get API key from environment
        if model.startswith("gemini"):
            api_key = api_key_list[0]
        else:
            api_key = api_key_list[1]
    
    # Determine model type and call appropriate function
    if model.startswith("gemini"):
        # Google Gemini models
        if not api_key:
            return json.dumps({
                "variants": [],
                "error": "Google API key not provided. Set GOOGLE_API_KEY environment variable."
            })
        
        result = call_google_model(
            model_name=model,
            prompt=prompt,
            api_key=api_key,
            timeout=120,
            parse_func=parse_json_response
        )
        
        if result["success"]:
            return json.dumps(result["output"])
        else:
            # Return error in JSON format
            return json.dumps({
                "variants": [],
                "error": result.get("error", "Unknown error")
            })
    
    elif ":" in model or model in ["deepseek-v3.1:671b-cloud", "gpt-oss:120b-cloud"]:
        # Ollama models (deepseek, gpt-oss, etc.)
        result = call_ollama_model(
            model=model,
            prompt=prompt,
            api_key=api_key or "",  # Ollama doesn't need API key
            parse_func=parse_json_response
        )
        
        if result["success"]:
            return json.dumps(result["output"])
        else:
            # Return error in JSON format
            return json.dumps({
                "variants": [],
                "error": result.get("error", "Unknown error")
            })
    else:
        # Unsupported model
        return json.dumps({
            "variants": [],
            "error": f"Unsupported model: {model}. Supported models: Gemini models (gemini-*) or Ollama models (deepseek-v3.1:671b-cloud, gpt-oss:120b-cloud, etc.)"
        })




import json
import time
import math
import ast
import tracemalloc
import resource
import subprocess
import tempfile
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# ============================================================================
# Configuration
# ============================================================================

@dataclass
class Config:
    max_iterations: int = 20
    model: str = "gpt-oss:120b-cloud"
    temperature_initial: float = 100.0
    temperature_final: float = 0.1
    weights: Dict[str, float] = None
    timeout: int = 5  # seconds
    memory_limit: int = 256  # MB
    verbose: bool = True
    enable_visualization: bool = True
    enable_backup: bool = True
    
    def __post_init__(self):
        if self.weights is None:
            self.weights = {
                "execution_time": 1.0,
                "memory_usage": 0.5,
                "test_failures": 100.0  # Very important: code must work correctly
            }


# ============================================================================
# Sandbox Execution
# ============================================================================

class Sandbox:
    """Secure code execution in isolated environment"""
    
    def __init__(self, timeout: int = 5, memory_limit_mb: int = 256):
        self.timeout = timeout
        self.memory_limit = memory_limit_mb * 1024 * 1024  # convert to bytes
    
    def execute(self, code: str, test_cases: List[Dict]) -> Dict:
        """
        Execute code with test cases
        
        Returns:
            {
                "success": bool,
                "execution_time": float,  # seconds
                "memory_usage": float,    # MB
                "tests_passed": int,
                "tests_failed": int,
                "errors": List[str]
            }
        """
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            # Add test code to end of file
            full_code = self._build_test_code(code, test_cases)
            f.write(full_code)
            temp_file = f.name
        
        try:
            # Execute code in subprocess with limits
            result = self._run_subprocess(temp_file)
            return result
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file)
            except:
                pass
    
    def _build_test_code(self, code: str, test_cases: List[Dict]) -> str:
        """Build complete code with tests"""
        test_code = f"""
import time
import tracemalloc
import json
import sys

# Main code
{code}

# Run tests
def run_tests():
    test_cases = {json.dumps(test_cases)}
    results = {{
        "tests_passed": 0,
        "tests_failed": 0,
        "errors": [],
        "execution_time": 0.0,
        "memory_usage": 0.0
    }}
    
    tracemalloc.start()
    start_time = time.perf_counter()
    
    try:
        for i, test in enumerate(test_cases):
            func_name = test["function"]
            inputs = test["input"]
            expected = test["expected"]
            
            try:
                # Execute function
                if func_name in globals():
                    func = globals()[func_name]
                    if isinstance(inputs, dict):
                        actual = func(**inputs)
                    elif isinstance(inputs, list):
                        actual = func(*inputs)
                    else:
                        actual = func(inputs)
                    
                    # Compare result
                    if actual == expected:
                        results["tests_passed"] += 1
                    else:
                        results["tests_failed"] += 1
                        results["errors"].append(
                            f"Test {{i}}: Expected {{expected}}, got {{actual}}"
                        )
                else:
                    results["tests_failed"] += 1
                    results["errors"].append(f"Function '{{func_name}}' not found")
            
            except Exception as e:
                results["tests_failed"] += 1
                results["errors"].append(f"Test {{i}} error: {{str(e)}}")
        
        end_time = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        results["execution_time"] = end_time - start_time
        results["memory_usage"] = peak / (1024 * 1024)  # MB
        
    except Exception as e:
        import traceback
        results["errors"].append(f"Fatal error: {{str(e)}}")
        # Still record timing even on error
        try:
            end_time = time.perf_counter()
            results["execution_time"] = end_time - start_time
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            results["memory_usage"] = peak / (1024 * 1024)  # MB
        except:
            pass
    
    # Always print JSON, even if there were errors
    print(json.dumps(results), flush=True)

if __name__ == "__main__":
    run_tests()
"""
        return test_code
    
    def _run_subprocess(self, filepath: str) -> Dict:
        """Execute file in subprocess with limits"""
        try:
            # Set resource limits (Linux/Unix only)
            def set_limits():
                try:
                    # CPU time limit
                    resource.setrlimit(resource.RLIMIT_CPU, (self.timeout, self.timeout))
                    # Memory limit
                    resource.setrlimit(resource.RLIMIT_AS, (self.memory_limit, self.memory_limit))
                except:
                    pass  # Doesn't work on Windows
            
            # Execute subprocess
            result = subprocess.run(
                ['python3', filepath],
                capture_output=True,
                text=True,
                timeout=self.timeout + 1,
                preexec_fn=set_limits if os.name != 'nt' else None
            )
            
            # Parse result
            if result.returncode == 0:
                if result.stdout and result.stdout.strip():
                    try:
                        output = json.loads(result.stdout.strip())
                        output["success"] = True
                        
                        # Map old key names to new ones for backward compatibility
                        if "passed" in output and "tests_passed" not in output:
                            output["tests_passed"] = output.pop("passed", 0)
                        if "failed" in output and "tests_failed" not in output:
                            output["tests_failed"] = output.pop("failed", 0)
                        
                        # Ensure all required keys exist with defaults
                        output.setdefault("tests_passed", 0)
                        output.setdefault("tests_failed", 0)
                        output.setdefault("execution_time", 0.0)
                        output.setdefault("memory_usage", 0.0)
                        output.setdefault("errors", [])
                        
                        return output
                    except json.JSONDecodeError as e:
                        return {
                            "success": False,
                            "execution_time": float('inf'),
                            "memory_usage": float('inf'),
                            "tests_passed": 0,
                            "tests_failed": 999,
                            "errors": [f"Failed to parse JSON output. stdout: {result.stdout[:200]}, stderr: {result.stderr[:200] if result.stderr else 'none'}. Error: {str(e)}"]
                        }
                else:
                    # Subprocess succeeded but no output - this shouldn't happen
                    return {
                        "success": False,
                        "execution_time": float('inf'),
                        "memory_usage": float('inf'),
                        "tests_passed": 0,
                        "tests_failed": 999,
                        "errors": [f"No output from subprocess. stderr: {result.stderr[:500] if result.stderr else 'none'}"]
                    }
            else:
                error_msg = result.stderr[:500] if result.stderr else "Unknown error"
                if result.stdout:
                    error_msg += f" | stdout: {result.stdout[:200]}"
                return {
                    "success": False,
                    "execution_time": float('inf'),
                    "memory_usage": float('inf'),
                    "tests_passed": 0,
                    "tests_failed": 999,
                    "errors": [error_msg]
                }
        
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "execution_time": float('inf'),
                "memory_usage": float('inf'),
                "tests_passed": 0,
                "tests_failed": 999,
                "errors": [f"Timeout: Execution exceeded {self.timeout}s"]
            }
        except Exception as e:
            return {
                "success": False,
                "execution_time": float('inf'),
                "memory_usage": float('inf'),
                "tests_passed": 0,
                "tests_failed": 999,
                "errors": [f"Execution error: {str(e)}"]
            }


# ============================================================================
# LLM Interface
# ============================================================================


def choose_model_for_optimization(current_metrics: Dict) -> str:
    random_number = random.random()
    if random_number < 0.5:
        return "gpt-oss:120b-cloud"
    elif random_number < 0.7:   # 671B
        return "deepseek-v3.1:671b-cloud"
    else:
        return "gemini-2.5-pro"
    

def build_prompt(code: str, test_cases: List[Dict], current_metrics: Dict, iteration: int) -> str:
    """Build prompt for LLM"""
    
    tests_str = "\n".join([
        f"  Test {i+1}: {t['function']}({t['input']}) → {t['expected']}"
        for i, t in enumerate(test_cases)
    ])
    
    metrics_str = f"""
  • Execution time: {current_metrics.get('execution_time', 'N/A')}s
  • Memory usage: {current_metrics.get('memory_usage', 'N/A')}MB
  • Tests passed: {current_metrics.get('tests_passed', 0)}/{current_metrics.get('tests_passed', 0) + current_metrics.get('tests_failed', 0)}
"""
    
    return f"""You are a Python code optimizer. Analyze this code and suggest ONE optimization.

**Current Code:**
```python
{code}
```

**Test Cases (your code MUST pass all of these):**
{tests_str}

**Current Performance:**
{metrics_str}

**Your Task:**
Suggest ONE code optimization that:
1. Passes ALL test cases (correctness is critical)
2. Improves execution time or memory usage
3. Maintains or improves code readability

**Respond in JSON format:**
{{
  "description": "Brief description of optimization",
  "code": "Complete optimized code",
  "reasoning": "Why this should be faster/more efficient"
}}

Return ONLY valid JSON, no markdown formatting."""


# ============================================================================
# Energy Calculation & Simulated Annealing
# ============================================================================

def calculate_energy(metrics: Dict, weights: Dict) -> float:
    """
    Calculate energy (lower = better)
    Scale values to make small differences meaningful
    """
    exec_time = metrics.get("execution_time", float('inf'))
    mem_usage = metrics.get("memory_usage", float('inf'))
    tests_failed = metrics.get("tests_failed", 999)
    
    # Scale time to microseconds for better precision (1 second = 1,000,000 units)
    # Scale memory to KB for better precision (1 MB = 1024 units)
    energy = (
        exec_time * 1000000 * weights["execution_time"] +  # Convert seconds to microseconds
        mem_usage * 1024 * weights["memory_usage"] +  # Convert MB to KB
        tests_failed * weights["test_failures"]
    )
    return energy


def get_temperature(iteration: int, max_iter: int, config: Config) -> float:
    """Calculate current temperature"""
    progress = iteration / max_iter
    T_initial = config.temperature_initial
    T_final = config.temperature_final
    # Exponential cooling
    return T_final + (T_initial - T_final) * math.exp(-5 * progress)


def should_accept(current_energy: float, new_energy: float, temperature: float) -> bool:
    """Decision to accept or reject"""
    
    # If improved, definitely accept
    if new_energy < current_energy:
        return True
    
    # If temperature is zero, only accept best
    if temperature <= 0:
        return False
    
    # Calculate acceptance probability for worse solution
    delta_energy = new_energy - current_energy
    probability = math.exp(-delta_energy / temperature)
    
    # Random decision
    import random
    return random.random() < probability


# ============================================================================
# Main Optimizer
# ============================================================================

def optimize(
    initial_code: str,
    test_cases: List[Dict],
    config: Config = None
) -> Dict:

    
    if config is None:
        config = Config()
    
    sandbox = Sandbox(timeout=config.timeout, memory_limit_mb=config.memory_limit)
    
    # Initialize visualizer and backup manager
    visualizer = None
    backup_manager = None
    
    if config.enable_visualization:
        try:
            visualizer = OptimizerVisualizer()
            if config.verbose:
                print("📊 Visualization enabled")
        except Exception as e:
            if config.verbose:
                print(f"⚠️  Warning: Could not initialize visualizer: {e}")
            visualizer = None
    
    if config.enable_backup:
        try:
            backup_manager = BackupManager()
            if config.verbose:
                print("💾 Real-time backup enabled")
        except Exception as e:
            if config.verbose:
                print(f"⚠️  Warning: Could not initialize backup manager: {e}")
            backup_manager = None
    
    # Evaluate initial code
    if config.verbose:
        print("=" * 70)
        print("🚀 Starting Code Optimization with Simulated Annealing")
        print("=" * 70)
        print(f"\n📝 Initial code ({len(initial_code.split())} lines)")
        print(f"🧪 Test cases: {len(test_cases)}")
        print(f"⚙️  Model: {config.model}")
        print(f"🔄 Max iterations: {config.max_iterations}\n")
    
    current_metrics = sandbox.execute(initial_code, test_cases)
    current_energy = calculate_energy(current_metrics, config.weights)
    current_code = initial_code
    
    # Initialize best solution
    best_code = current_code
    best_energy = current_energy
    best_metrics = current_metrics.copy()
    
    if config.verbose:
        exec_time = current_metrics.get('execution_time', 0.0)
        mem_usage = current_metrics.get('memory_usage', 0.0)
        tests_passed = current_metrics.get('tests_passed', 0)
        tests_failed = current_metrics.get('tests_failed', 0)
        total_tests = tests_passed + tests_failed
        
        # Format time with appropriate precision
        if exec_time < 0.0001:
            time_str = f"{exec_time*1000000:.2f}μs"  # microseconds
        elif exec_time < 0.001:
            time_str = f"{exec_time*1000:.3f}ms"  # milliseconds
        elif exec_time < 1:
            time_str = f"{exec_time*1000:.2f}ms"  # milliseconds
        else:
            time_str = f"{exec_time:.4f}s"
        
        # Format memory with appropriate units
        if mem_usage < 0.001:
            mem_str = f"{mem_usage*1024:.2f}KB"  # kilobytes
        elif mem_usage < 1:
            mem_str = f"{mem_usage:.3f}MB"
        else:
            mem_str = f"{mem_usage:.2f}MB"
        
        print(f"📊 Baseline metrics:")
        print(f"   ⏱️  Time: {time_str}")
        print(f"   💾 Memory: {mem_str}")
        print(f"   ✅ Tests: {tests_passed}/{total_tests}")
        if current_metrics.get('errors'):
            print(f"   ⚠️  Errors: {len(current_metrics.get('errors', []))}")
        # Format energy with appropriate precision
        if current_energy < 0.01:
            energy_str = f"{current_energy:.6f}"
        elif current_energy < 1:
            energy_str = f"{current_energy:.4f}"
        else:
            energy_str = f"{current_energy:.2f}"
        print(f"   ⚡ Energy: {energy_str}\n")
    
    history = [{
        "iteration": 0,
        "energy": current_energy,
        "metrics": current_metrics,
        "temperature": config.temperature_initial,
        "accepted": True,
        "is_best": True,
        "llm_idea": "Baseline (no optimization)",  # ✅ Added
        "llm_reasoning": "Initial code",
        "estimated_improvement": "0%",
        "actual_time_change": "N/A",
        "actual_mem_change": "N/A"
    }]
    
    # Update visualizer with initial state
    if visualizer:
        try:
            visualizer.update(history[0])
        except Exception as e:
            if config.verbose:
                print(f"⚠️  Warning: Could not update visualizer: {e}")
    
    # Backup initial code (after initial evaluation)
    if backup_manager:
        try:
            backup_manager.backup_code(initial_code, current_metrics, current_energy, 0, history[0])
            if config.verbose:
                print(f"💾 Initial code backed up")
        except Exception as e:
            if config.verbose:
                print(f"⚠️  Warning: Could not backup initial code: {e}")
    
    # Main optimization loop
    for iteration in range(1, config.max_iterations + 1):
        temp = get_temperature(iteration, config.max_iterations, config)
        
        if config.verbose:
            print(f"{'='*70}")
            print(f"🔄 Iteration {iteration}/{config.max_iterations} (T={temp:.1f})")
            print(f"{'='*70}")
        
        try:
            # ===== Use improved prompt =====
            strategy = select_strategy(iteration, config.max_iterations, current_code, history)
            prompt = build_improved_prompt(
                code=current_code, 
                test_cases=test_cases, 
                current_metrics=current_metrics, 
                iteration=iteration, 
                history=history,  # ✅ Added
                strategy=strategy  # ✅ Added
            )
            
            
            # Select model (if you have choose_model_for_optimization function)
            config.model = choose_model_for_optimization(current_metrics)
            print("########################################################")
            print(f"💡 Model: {config.model}")
            print("########################################################")
            print(f"💡 Strategy: {strategy}")
            print("########################################################")
            print(f"💡 Prompt: {history}")
            print("########################################################")

            
            response = call_llm(prompt, config.model)
            
            # Parse response
            try:
                suggestion = json.loads(response)
                new_code = suggestion.get("code", "")
                
                # ===== Save LLM information =====
                llm_idea = suggestion.get("strategy", suggestion.get("description", "Unknown optimization"))
                llm_reasoning = suggestion.get("reasoning", "No reasoning provided")
                estimated_improvement = suggestion.get("estimated_improvement", "Unknown")
                
                if not new_code:
                    if config.verbose:
                        print("⚠️  No code in LLM response, skipping...")
                    continue
                
                if config.verbose:
                    print(f"💡 Strategy: {llm_idea}")
                    print(f"📝 Reasoning: {llm_reasoning[:80]}...")
                    print(f"📊 Estimated Improvement: {estimated_improvement}")
                
            except json.JSONDecodeError:
                if config.verbose:
                    print("⚠️  Failed to parse LLM response, skipping...")
                continue
            
            # Execute and evaluate new code
            new_metrics = sandbox.execute(new_code, test_cases)
            new_energy = calculate_energy(new_metrics, config.weights)
            
            # ===== Calculate actual changes =====
            time_change = _calculate_change(
                current_metrics.get('execution_time', 0),
                new_metrics.get('execution_time', 0)
            )
            mem_change = _calculate_change(
                current_metrics.get('memory_usage', 0),
                new_metrics.get('memory_usage', 0)
            )
            
            if config.verbose:
                exec_time = new_metrics.get('execution_time', 0.0)
                mem_usage = new_metrics.get('memory_usage', 0.0)
                tests_passed = new_metrics.get('tests_passed', 0)
                tests_failed = new_metrics.get('tests_failed', 0)
                total_tests = tests_passed + tests_failed
                
                # Format time with appropriate precision
                if exec_time < 0.0001:
                    time_str = f"{exec_time*1000000:.2f}μs"  # microseconds
                elif exec_time < 0.001:
                    time_str = f"{exec_time*1000:.3f}ms"  # milliseconds
                elif exec_time < 1:
                    time_str = f"{exec_time*1000:.2f}ms"  # milliseconds
                else:
                    time_str = f"{exec_time:.4f}s"
                
                # Format memory with appropriate units
                if mem_usage < 0.001:
                    mem_str = f"{mem_usage*1024:.2f}KB"  # kilobytes
                elif mem_usage < 1:
                    mem_str = f"{mem_usage:.3f}MB"
                else:
                    mem_str = f"{mem_usage:.2f}MB"
                
                print(f"📊 New metrics:")
                print(f"   ⏱️  Time: {time_str} ({time_change})")  # ✅ Added
                print(f"   💾 Memory: {mem_str} ({mem_change})")  # ✅ Added
                print(f"   ✅ Tests: {tests_passed}/{total_tests}")
                if new_metrics.get('errors'):
                    print(f"   ⚠️  Errors: {len(new_metrics.get('errors', []))}")
                # Format energy with appropriate precision
                if new_energy < 0.01:
                    energy_str = f"{new_energy:.6f}"
                elif new_energy < 1:
                    energy_str = f"{new_energy:.4f}"
                else:
                    energy_str = f"{new_energy:.2f}"
                print(f"   ⚡ Energy: {energy_str}")
            
            # Decision to accept or reject
            accepted = should_accept(current_energy, new_energy, temp)
            
            if accepted:
                current_code = new_code
                current_metrics = new_metrics
                current_energy = new_energy
                
                # Update best solution
                if new_energy < best_energy:
                    best_code = new_code
                    best_energy = new_energy
                    best_metrics = new_metrics.copy()
                    is_best = True
                    if config.verbose:
                        delta = new_energy - current_energy
                        if abs(delta) < 0.01:
                            delta_str = f"{delta:.6f}"
                        elif abs(delta) < 1:
                            delta_str = f"{delta:.4f}"
                        else:
                            delta_str = f"{delta:.2f}"
                        print(f"✨ NEW BEST! (ΔE = {delta_str})")
                else:
                    is_best = False
                    if config.verbose:
                        delta = new_energy - current_energy
                        if abs(delta) < 0.01:
                            delta_str = f"{delta:.6f}"
                        elif abs(delta) < 1:
                            delta_str = f"{delta:.4f}"
                        else:
                            delta_str = f"{delta:.2f}"
                        print(f"✅ Accepted (ΔE = {delta_str})")
            else:
                is_best = False
                if config.verbose:
                    delta = new_energy - current_energy
                    prob = math.exp(-delta / temp) if temp > 0 else 0
                    if abs(delta) < 0.01:
                        delta_str = f"{delta:.6f}"
                    elif abs(delta) < 1:
                        delta_str = f"{delta:.4f}"
                    else:
                        delta_str = f"{delta:.2f}"
                    print(f"❌ Rejected (ΔE = {delta_str}, P_accept = {prob:.3f})")
            
            # ===== Save to history with complete information =====
            history_entry = {
                "iteration": iteration,
                "energy": current_energy,
                "metrics": current_metrics.copy(),
                "temperature": temp,
                "accepted": accepted,
                "is_best": is_best,
                "llm_idea": llm_idea,  # ✅ Added
                "llm_reasoning": llm_reasoning,  # ✅ Added
                "estimated_improvement": estimated_improvement,  # ✅ Added
                "actual_time_change": time_change,  # ✅ Added
                "actual_mem_change": mem_change  # ✅ Added
            }
            history.append(history_entry)
            
            # ===== Update visualizer =====
            if visualizer:
                try:
                    visualizer.update(history_entry)
                except Exception as e:
                    if config.verbose:
                        print(f"⚠️  Warning: Could not update visualizer: {e}")
            
            # ===== Backup best code =====
            if backup_manager and is_best:
                try:
                    backup_path = backup_manager.backup_code(
                        best_code, best_metrics, best_energy, iteration, history_entry
                    )
                    if backup_path and config.verbose:
                        print(f"💾 Best code backed up: {backup_path}")
                except Exception as e:
                    if config.verbose:
                        print(f"⚠️  Warning: Could not backup code: {e}")
            
        except Exception as e:
            if config.verbose:
                print(f"⚠️  Error in iteration {iteration}: {str(e)}")
            continue
    
    # Calculate improvement
    initial_energy = history[0]["energy"]
    
    # Calculate improvement with better handling of small values
    if initial_energy > 0:
        improvement = ((initial_energy - best_energy) / initial_energy * 100)
    elif initial_energy == best_energy == 0:
        # Both are essentially zero - check if there's any measurable difference
        initial_time = history[0]["metrics"].get('execution_time', 0)
        best_time = best_metrics.get('execution_time', 0)
        initial_mem = history[0]["metrics"].get('memory_usage', 0)
        best_mem = best_metrics.get('memory_usage', 0)
        
        # Calculate improvement based on actual metrics
        time_improvement = ((initial_time - best_time) / initial_time * 100) if initial_time > 0 else 0
        mem_improvement = ((initial_mem - best_mem) / initial_mem * 100) if initial_mem > 0 else 0
        improvement = max(time_improvement, mem_improvement)
    else:
        improvement = 0
    
    if config.verbose:
        # Format energy with appropriate precision
        def format_energy(e):
            if e == 0:
                return "0.00"
            elif e < 0.0001:
                return f"{e*1000000:.2f}μ"
            elif e < 0.01:
                return f"{e*1000:.3f}m"
            else:
                return f"{e:.4f}"
        
        print(f"\n{'='*70}")
        print("🎉 OPTIMIZATION COMPLETE")
        print(f"{'='*70}")
        print(f"📈 Improvement: {improvement:.2f}%")
        print(f"⚡ Energy: {format_energy(initial_energy)} → {format_energy(best_energy)}")
        # Format time and memory for display
        def format_time(t):
            if t < 0.0001:
                return f"{t*1000000:.2f}μs"
            elif t < 0.001:
                return f"{t*1000:.3f}ms"
            elif t < 1:
                return f"{t*1000:.2f}ms"
            else:
                return f"{t:.4f}s"
        
        def format_memory(m):
            if m < 0.001:
                return f"{m*1024:.2f}KB"
            elif m < 1:
                return f"{m:.3f}MB"
            else:
                return f"{m:.2f}MB"
        
        initial_time = history[0]['metrics'].get('execution_time', 0)
        best_time = best_metrics.get('execution_time', 0)
        initial_mem = history[0]['metrics'].get('memory_usage', 0)
        best_mem = best_metrics.get('memory_usage', 0)
        
        print(f"⏱️  Time: {format_time(initial_time)} → {format_time(best_time)}")
        print(f"💾 Memory: {format_memory(initial_mem)} → {format_memory(best_mem)}")
        
        # ===== Display best optimizations =====
        print(f"\n{'='*70}")
        print("🏆 TOP OPTIMIZATIONS:")
        print(f"{'='*70}")
        
        # Find best ones
        successful = [h for h in history[1:] if h.get('accepted') and h['metrics'].get('tests_failed', 0) == 0]
        if successful:
            top_3 = sorted(successful, key=lambda x: x['energy'])[:3]
            for rank, h in enumerate(top_3, 1):
                iter_num = h['iteration']
                idea = h.get('llm_idea', 'Unknown')
                time_ch = h.get('actual_time_change', 'N/A')
                mem_ch = h.get('actual_mem_change', 'N/A')
                print(f"{rank}. Iteration {iter_num}: {idea}")
                print(f"   └─ Time: {time_ch}, Memory: {mem_ch}")
        
        # Save final plot
        if visualizer:
            try:
                plot_path = visualizer.save_plot()
                print(f"\n📊 Final plot saved: {plot_path}")
            except Exception as e:
                if config.verbose:
                    print(f"⚠️  Warning: Could not save final plot: {e}")
        
        # Final backup message
        if backup_manager:
            latest_backup = backup_manager.get_latest_backup()
            if latest_backup:
                print(f"\n💾 Latest backup: {latest_backup.get('filepath', 'N/A')}")
    
    # Cleanup
    if visualizer:
        try:
            # Don't close immediately - let user see the final plot
            if config.verbose:
                print(f"\n📊 Visualization window remains open. Close manually or it will close when script exits.")
        except:
            pass
    
    return {
        "best_code": best_code,
        "best_energy": best_energy,
        "best_metrics": best_metrics,
        "initial_metrics": history[0]["metrics"],
        "improvement": improvement,
        "history": history
    }


# ============================================================================
# Helper Function for calculating changes
# ============================================================================

def _calculate_change(old_value: float, new_value: float) -> str:
    """
    Calculate percentage change and display with symbol
    Positive (decrease) = better ✓
    Negative (increase) = worse ✗
    """
    if old_value == 0 or old_value == float('inf'):
        return "N/A"
    
    # Calculate percentage decrease (positive = better)
    change_percent = ((old_value - new_value) / old_value) * 100
    
    if abs(change_percent) < 0.1:
        return "±0%"
    elif change_percent > 0:
        return f"-{abs(change_percent):.1f}% ✓"  # Decrease = good
    else:
        return f"+{abs(change_percent):.1f}% ✗"  # Increase = bad
# ============================================================================
# Example Usage
# ============================================================================

def main():
    with open("data.json", "r") as f:
        data = json.load(f)

    index= 4
    initial_code = data[index]["initial_code"]
    test_cases = data[index]["test_cases"]
    
   
    
    config = Config(
        max_iterations=40,  # Maximum optimization iterations for hardest optimization
        verbose=True,
        timeout=10,  # Increased timeout for complex optimizations
        memory_limit=512  # Increased memory limit
    )
    
    result = optimize(initial_code, test_cases, config)
    
    print(f"\n{'='*70}")
    print("💻 OPTIMIZED CODE:")
    print(f"{'='*70}")
    print(result["best_code"])
    with open("o1.py", "w") as f:
        f.write(result["best_code"])


if __name__ == "__main__":
    main()