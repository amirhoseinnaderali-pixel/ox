# Failure analysis

Primary failure taxonomy:
syntax failure; import failure; runtime failure; timeout; memory failure; incorrect output; edge-case failure; regression; invalid optimization; no measurable gain; benchmark noise; premature optimization; algorithmically worse transformation; prompt/model failure; serialization/parsing failure.

A failed run must remain in raw results. Failure analysis should use proposal-level records rather than only final summaries.

For each failure retain problem, model, seed, budget, iteration, strategy, candidate correctness diagnostics, runtime diagnostics, and acceptance reason.
