# Ablation matrix

A1: single-shot versus iterative.
A2: verification disabled as a diagnostic safety study; never use this to accept incorrect candidates in the main system.
A3: remove simulated annealing.
A4: remove strategy conditioning.
A5: remove optimization history.
A6: hold model family fixed.
A7: compare alternative model identifiers under equal budgets.
A8: budgets 1, 5, 10, 20, 50.
A9: small, medium, large input regimes.
A10: greedy versus simulated-annealing acceptance.

Every ablation must keep the remaining variables fixed and write raw JSONL results.
