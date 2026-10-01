# Complete Optim Project Documentation

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Project Structure](#project-structure)
3. [Main Components](#main-components)
4. [Optimization Algorithm](#optimization-algorithm)
5. [OX vs AI Comparison](#ox-vs-ai-comparison)
6. [Important Files](#important-files)
7. [Usage Guide](#usage-guide)

---

## Project Overview

This project is an **automated Python code optimization system** that uses **Artificial Intelligence (LLM)** to improve code performance. The project consists of two main parts:

### 1. **Code Optimizer with LLM**
   - Uses various LLM models (Gemini, DeepSeek, GPT-OSS) for optimization suggestions
   - **Simulated Annealing** algorithm for decision-making on accepting or rejecting changes
   - Code execution in isolated environment (Sandbox) for security
   - Real-time visualization of optimization progress
   - Automatic backup of best code versions

### 2. **OX vs AI Comparison**
   - Compares manually optimized solutions (OX) with AI-generated solutions
   - 5 different algorithmic problems
   - Performance, speed, and memory consumption comparison

---

## Project Structure

```
optim/
├── optimizer.py              # Main optimizer file
├── api.py                    # API interface for LLM models
├── backup_manager.py         # Automatic backup management
├── visualizer.py             # Progress visualization
├── data.json                 # Problem data (5 algorithmic problems)
├── requirements.txt          # Project dependencies
│
├── backups/                  # Automatic backups
│   ├── 2025-11-23/          # Date-stamped backups
│   ├── backup_index.json    # Backup index
│   └── latest_best_code.py  # Latest optimized code
│
├── optimizer_plots/          # Progress charts
│   └── optimizer_progress_*.png
│
├── ox-vs-ai/                # OX vs AI comparison section
│   ├── solutions/            # Optimized solutions (OX)
│   │   ├── 001_3sum.py
│   │   ├── 002_lcs.py
│   │   ├── 003_subarray_sum.py
│   │   ├── 004_duplicate_pairs.py
│   │   └── 005_matrix_path_sum.py
│   ├── ai_failures/          # AI error examples
│   └── README.md
│
└── problem0/ to problem4/    # Comparison results for each problem
    ├── ox.py                 # OX solution
    ├── claude4.5.py          # Claude 4.5 solution
    ├── grok4.1.py            # Grok 4.1 solution
    ├── compare.py            # Comparison script
    └── results.json          # Comparison results
```

---

## Main Components

### 1. **optimizer.py** - Main Optimization Engine

#### Features:
- **Simulated Annealing**: Physics-inspired optimization algorithm
- **Multi-Strategy Optimization**: Various optimization strategies:
  - `algorithmic`: Reduce algorithmic complexity (O(n²) → O(n))
  - `data_structures`: Optimize data structures (list → set/dict)
  - `comprehensions`: Use List/Dict Comprehensions
  - `caching`: Remove redundant computations
  - `early_exit`: Early exit from loops
  - `vectorization`: Use Python built-in functions

#### Important Classes and Functions:

**`Config`**: Optimizer settings
```python
- max_iterations: Maximum number of iterations (default: 20)
- model: LLM model to use
- temperature_initial/final: Initial/final temperature for Simulated Annealing
- weights: Evaluation metric weights
- timeout: Execution time limit
- memory_limit: Memory limit
```

**`Sandbox`**: Secure execution environment
- Code execution in separate subprocess
- Time and memory limits
- Test execution and metric collection

**`optimize()`**: Main optimization function
- Receives initial code and tests
- Optimization loop with LLM
- Energy calculation and decision-making
- Save best code

#### Energy Calculation:
```python
Energy = (execution_time × 1,000,000 × weight_time) + 
         (memory_usage × 1,024 × weight_memory) + 
         (tests_failed × weight_failures)
```
Lower Energy means better code.

#### Simulated Annealing:
- Initially (high temperature): Higher probability of accepting worse changes
- Finally (low temperature): Only better changes are accepted
- Formula: `P(accept) = exp(-ΔE / T)`

---

### 2. **api.py** - LLM API Interface

#### Supported Models:
- **Google Gemini**: `gemini-2.5-pro`, `gemini-pro-latest`
- **Ollama Models**: `deepseek-v3.1:671b-cloud`, `gpt-oss:120b-cloud`

#### Functions:
- `chat_completion()`: Communication with Ollama API
- `call_google_model()`: Communication with Google Gemini API
- `call_ollama_model()`: Communication with Ollama models
- `parse_json_response()`: Parse JSON response from LLM

---

### 3. **backup_manager.py** - Backup Management

#### Features:
- Automatic backup of best code versions
- Save Metadata (metrics, iteration, improvement)
- Maintain backup index in `backup_index.json`
- Backup count limit (default: 100)
- `latest_best_code.py` file always contains the latest optimized code

#### Backup Structure:
```
backups/
├── best_code_iter_0012_20251123_143022.py    # Code
├── best_code_iter_0012_20251123_143022.json  # Metadata
└── latest_best_code.py                       # Latest code
```

---

### 4. **visualizer.py** - Visualization

#### Charts:
1. **Execution Time vs Iteration**: Execution time per iteration
2. **Memory Usage vs Iteration**: Memory consumption per iteration
3. **Energy vs Iteration**: Energy per iteration
4. **Accept/Reject Status**: Change acceptance/rejection status
5. **Statistics Panel**: Overall optimization statistics

#### Features:
- Real-time updates
- Display best values with green line
- Automatic final chart saving

---

### 5. **data.json** - Problem Data

Contains 5 algorithmic problems:

1. **Problem 0: Find Triplets with Sum Zero**
   - Initial code: O(N³) brute force
   - Goal: Convert to O(N²) with two-pointer

2. **Problem 1: Longest Common Subsequence**
   - Initial code: O(2^min(m,n)) recursive
   - Goal: Convert to O(m×n) with Dynamic Programming

3. **Problem 2: Count Subarrays with Target Sum**
   - Initial code: O(N²) nested loops
   - Goal: Convert to O(N) with prefix sum + hash map

4. **Problem 3: Find All Duplicate Value Pairs**
   - Initial code: O(N²) brute force
   - Goal: Convert to O(N) with hash map

5. **Problem 4: Matrix Maximum Path Sum**
   - Initial code: O(2^(m+n)) recursive
   - Goal: Convert to O(m×n) with Dynamic Programming

Each problem includes:
- `initial_code`: Inefficient initial code
- `test_cases`: Required tests
- `optimization_goal`: Optimization goal

---

## Optimization Algorithm

### Workflow:

```
1. Evaluate initial code
   ↓
2. Optimization loop (up to max_iterations):
   ├─ Select optimization strategy
   ├─ Build Prompt for LLM
   ├─ Receive suggestion from LLM
   ├─ Execute new code in Sandbox
   ├─ Calculate new Energy
   ├─ Decision-making (Simulated Annealing)
   ├─ Update best code (if improved)
   ├─ Visualization (Visualizer)
   └─ Backup (BackupManager)
   ↓
3. Return best code and results
```

### Prompt Engineering:

Prompt includes:
- Current code
- Required tests
- Current metrics (time, memory, tests)
- History of successful/failed optimizations
- Specific strategy guide
- Few-Shot Learning examples

### Optimization Strategies:

1. **Iteration 0-30%**: `algorithmic` (highest impact)
2. **Iteration 30-50%**: `data_structures`
3. **Iteration 50-100%**: Rotate between remaining strategies

---

## OX vs AI Comparison

### Overall Results:

| Model       | Tests Passed | Avg Time (s) | Memory (MB) | Status |
|-------------|--------------|--------------|-------------|--------|
| **OX**      | **14/14** ✅ | **2.18e-05** ⚡ | **0.00050** 💾 | Winner |
| Claude 4.5  | 14/14 ✅     | 3.99e-05 🐌  | 0.00052     | Success |
| Grok 4.1    | 12/14 ❌     | 5.50e-05 🐌🐌 | 0.00084 💾💾 | Error |

### Problem Details:

#### Problem 0: 3Sum
- OX: 1.47e-05s (fastest)
- Claude 4.5: 1.76e-05s
- Grok 4.1: 1.70e-05s

#### Problem 1: LCS
- OX: 2.50e-05s (3.6x faster)
- Claude 4.5: 9.08e-05s
- Grok 4.1: 8.73e-05s

#### Problem 2: Subarray Sum
- OX: 1.36e-05s (fastest)
- Claude 4.5: 1.49e-05s
- Grok 4.1: 1.98e-05s

#### Problem 3: Duplicate Pairs
- OX: 2.76e-05s ✅
- Claude 4.5: 4.59e-05s ✅
- Grok 4.1: ❌ **2 test failures** (tuple instead of list)

#### Problem 4: Matrix Path
- OX: 1.78e-05s (fastest)
- Claude 4.5: 2.37e-05s
- Grok 4.1: 2.37e-05s

### Important Notes:

1. **OX** was fastest in all problems
2. **Grok 4.1** had an error in Problem 3 (wrong data type)
3. **OX** used advanced techniques:
   - Bit-parallel algorithms
   - Local variable binding
   - Early exit optimizations
   - Low-level optimizations

---

## Important Files

### Main Files:

1. **optimizer.py** (1472 lines)
   - `Config` class: Settings
   - `Sandbox` class: Secure execution
   - `optimize()` function: Main optimization
   - Helper functions: Energy, Temperature, Strategy Selection

2. **api.py** (62 lines)
   - LLM API communication
   - Support for Gemini and Ollama

3. **backup_manager.py** (168 lines)
   - Automatic backup management
   - Metadata storage

4. **visualizer.py** (253 lines)
   - Real-time progress display
   - 5 different charts

5. **data.json** (152 lines)
   - 5 algorithmic problems
   - Initial codes and tests

### Comparison Files:

- `ox-vs-ai/solutions/`: Optimized OX solutions
- `problem0/` to `problem4/`: Comparison results
- `model_comparison_summary.md`: Results summary

---

## Usage Guide

### 1. Install Dependencies:

```bash
pip install -r requirements.txt
```

Main dependencies:
- `matplotlib`: For visualization
- `requests`: For API calls
- `google-genai`: For Gemini API

### 2. Setup Ollama (for Ollama models):

```bash
# Install Ollama
# Download models:
ollama pull deepseek-v3.1:671b-cloud
ollama pull gpt-oss:120b-cloud
```

### 3. Configure API Keys:

In `optimizer.py`:
```python
api_key_list = [
    "YOUR_GOOGLE_API_KEY_1",
    "YOUR_GOOGLE_API_KEY_2",
    ...
]
```

### 4. Run Optimizer:

```python
from optimizer import optimize, Config
import json

# Load data
with open("data.json", "r") as f:
    data = json.load(f)

# Select problem
problem_index = 0
initial_code = data[problem_index]["initial_code"]
test_cases = data[problem_index]["test_cases"]

# Configuration
config = Config(
    max_iterations=20,
    model="gpt-oss:120b-cloud",
    verbose=True,
    timeout=10,
    memory_limit=512
)

# Run optimization
result = optimize(initial_code, test_cases, config)

# Display result
print(f"Improvement: {result['improvement']:.2f}%")
print(f"Optimized code:")
print(result["best_code"])
```

### 5. Run OX vs AI Comparison:

```bash
cd problem0
python compare.py
```

---

## Optimization Techniques Used

### In OX Solutions:

1. **Local Variable Binding**:
   ```python
   append_res = result.append  # Faster than result.append()
   ```

2. **Early Exit**:
   ```python
   if a > 0:
       break  # Early exit
   ```

3. **Skip Duplicates**:
   ```python
   while left < right and arr[left] == b:
       left += 1
   ```

4. **Two-Pointer Technique**: For complexity reduction

5. **Sorting + Hash Map**: Combining techniques

---

## Results and Achievements

### Project Achievements:

1. ✅ Automated optimization system with LLM
2. ✅ Simulated Annealing algorithm for decision-making
3. ✅ Real-time visualization
4. ✅ Automatic backup
5. ✅ Successful OX vs AI comparison (OX won!)

### Technical Notes:

- **Sandbox Execution**: Secure code execution in subprocess
- **Multi-Model Support**: Support for multiple LLM models
- **Strategy Selection**: Intelligent strategy selection
- **History Context**: Using history in Prompt
- **Energy Calculation**: Accurate Energy calculation with appropriate scale

---

## Issues and Limitations

### Current Limitations:

1. **Timeout**: Complex code may timeout
2. **Memory Limit**: Memory limit for large code
3. **LLM Quality**: Optimization quality depends on LLM model
4. **Cost**: Using paid APIs (Gemini)

### Observed Issues:

- **Grok 4.1**: Data type error (tuple instead of list)
- **LLM Responses**: Sometimes invalid JSON responses
- **Timeout**: In very complex code

---

## Project Future

### Improvement Suggestions:

1. Support for more models
2. Multi-objective optimization
3. Learning from history (Meta-learning)
4. Support for other languages (C++, Rust)
5. CI/CD integration

---

## Summary

This project is a **comprehensive code optimization system** that:
- Uses **LLM** for optimization suggestions
- Makes decisions with **Simulated Annealing**
- Has **Real-time visualization**
- **Auto-backup** of best code versions
- Compared **OX** (manual solution) with **AI** and won!

---

**Author**: Amir Hosein  
**Date**: 2025  
**Language**: Python 3  
**Goal**: Automated code optimization using artificial intelligence
