from __future__ import annotations

STRATEGIES = {
    "algorithmic": "Reduce asymptotic complexity or improve the dominant algorithm.",
    "data_structures": "Replace costly data structures or lookups with more suitable ones.",
    "caching": "Eliminate repeated computation with safe memoization or reuse.",
    "early_exit": "Reduce unnecessary work through safe early termination or short-circuiting.",
    "vectorization": "Prefer efficient standard-library or vectorized operations when semantics are unchanged.",
    "local_micro": "Apply local Python-level optimizations only after larger algorithmic options are considered.",
    "memory": "Reduce peak memory while preserving output semantics and runtime feasibility.",
}

def strategy_prompt(strategy: str) -> str:
    if strategy not in STRATEGIES:
        raise KeyError(strategy)
    return STRATEGIES[strategy]
