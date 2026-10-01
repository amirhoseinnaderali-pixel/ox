# OX vs Claude 4.5 vs Grok 4.1

**5 algorithmic problems | Real benchmark | Pure Python**

## Results

| Model       | Tests Passed | Avg Time (s)  | Memory (MB) | Notes                     |
|-------------|--------------|---------------|-------------|---------------------------|
| **OX**      | **14/14** ✅ | **2.18e-05** ⚡ | **0.00050** 💾 | Fastest in every problem  |
| Claude 4.5  | 14/14 ✅     | 3.99e-05 🐌   | 0.00052     | Correct but slower        |
| Grok 4.1    | **12/14** ❌ | 5.50e-05 🐌🐌 | 0.00084 💾💾 | Failed 2 tests (Problem 3)|

### Problem 3 Failures (Grok 4.1)

- Returned `[[(0, 1), ...]]` instead of `[[0, 1], ...]` (doesn't know `list()`?)
- `TypeError: '<' not supported between instances of 'itertools.combinations'`

## Files

- `problem_0_*` through `problem_4_*` → `problem_X_ox.py` (fastest), `problem_X_claude4.5.py`, `problem_X_grok4.1.py`, `problem_X_results.json`
- `optimizer_plots/` → Performance charts

## Reproduce

```bash
python problem_0_compare.py
```

**OX wins.** 🏆 Fastest, most efficient, zero errors. Grok 4.1 failed because it can't convert tuple to list. 🤡
