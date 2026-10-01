# VEPO-LLM

## Verified Execution-guided Program Optimization with Large Language Models

VEPO-LLM is an executable research framework for studying whether large language models can iteratively improve executable programs when every proposal is subjected to objective execution-based verification.

Research question:
How effectively can LLMs improve executable program performance through iterative proposal, execution, verification, and acceptance under a fixed computational budget?

Primary hypothesis:
Iterative execution-verified LLM optimization can improve program performance while preserving functional correctness, with diminishing returns as optimization budget increases.

Secondary hypotheses:
- H1: iterative optimization outperforms single-shot optimization
- H2: execution verification reduces correctness regressions
- H3: algorithmic transformations yield larger gains than local micro-optimizations
- H4: larger budgets improve performance until saturation
- H5: different models exhibit different optimization strengths and failure modes
- H6: optimization efficiency depends on model capability and verification/acceptance strategy

These are hypotheses, not established findings.

Method:
Initial Program -> Proposal Generator -> Candidate -> Static Validation -> Execution Verification -> Performance Measurement -> Acceptance/Rejection -> Next Iteration.

Correctness is a hard constraint. A faster incorrect program is never accepted.

Formal objective:
Let P0 be the original program, Pi a candidate, V(P) the correctness verifier, F(P) the performance measurement, B the proposal budget, M the proposal model, and A the acceptance policy. A candidate must satisfy V(Pi)=correct before performance can affect acceptance. Runtime is the primary performance objective; memory is recorded separately. The historical weighted energy function is not the scientific objective of the new framework.

Benchmarking correction:
Historical timing values were on the order of 10^-5 seconds and are vulnerable to interpreter overhead and measurement noise. VEPO-LLM uses larger deterministic input regimes, warm-up runs, repeated measurements, medians, dispersion, and explicit environment metadata. The executor reports Python allocation peak separately from process RSS.

Benchmark suite:
- triplets_001: unique three-sum triplets
- lcs_001: LCS length
- subarray_sum_001: target-sum subarray counting
- duplicate_pairs_001: equal-value index pairs
- matrix_path_001: maximum path sum

Baselines:
1. original program
2. single-shot LLM
3. iterative LLM
4. iterative + execution verification
5. simulated-annealing acceptance
6. strong manually engineered reference implementation

The reference implementation is not claimed to be globally optimal.

Ablations:
A1 single-shot; A2 no verification diagnostic; A3 no simulated annealing; A4 no strategy conditioning; A5 no history; A6 single model; A7 alternative models; A8 budget 1/5/10/20/50; A9 benchmark scale; A10 acceptance policy.

Historical evidence:
The previous OX/Claude/Grok comparison remains under legacy/historical_comparison. It is explicitly labeled exploratory historical material and is not treated as controlled evidence.

Security:
Generated code is executed. The local executor uses subprocess and resource limits as defense in depth, not as a complete adversarial sandbox. Untrusted workloads should run inside a separately isolated container or VM with network and filesystem restrictions. Never commit credentials.

Reproduction:
python -m pip install -e '.[test]'
pytest

Research status:
Framework and tests implemented. Controlled LLM model comparison, large-scale ablations, statistical claims, and publication conclusions are not yet evaluated.

See docs/methodology.md, docs/benchmark.md, docs/ablations.md, docs/failure_analysis.md, docs/reproducibility.md, docs/research_positioning.md, and docs/paper.md.
