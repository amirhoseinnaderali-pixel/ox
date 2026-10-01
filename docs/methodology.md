# Methodology

The optimization problem is constrained search over executable programs. Proposal generation and acceptance are separate variables.

A candidate proceeds through:
1. syntax validation
2. execution-based correctness tests
3. performance measurement on deterministic larger inputs
4. acceptance policy

Correctness failure stops the pipeline. Performance cannot rescue an incorrect candidate.

Search generation variables include model, prompt strategy, history context, and proposal budget. Acceptance variables include greedy best-so-far and simulated annealing.

Runtime should be measured in-process after warm-up using repeated perf_counter_ns samples. Report median and dispersion. The benchmark should be large enough that a useful signal is not dominated by interpreter startup or timer granularity.

Do not collapse runtime and memory into an arbitrary scalar objective for primary analysis. If a secondary weighted score is explored, its exact equation and sensitivity analysis must be documented.

Every proposal receives a machine-readable record, including failure type when it fails.
