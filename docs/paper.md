# VEPO-LLM: Verified Execution-guided Program Optimization with Large Language Models

## Abstract
Not yet evaluated.

## 1. Introduction
LLMs can propose executable code transformations, but proposed code must be correct and measurably efficient. VEPO-LLM studies iterative optimization as a controlled search problem with execution-based verification.

## 2. Research Questions
See README for the ten primary and secondary questions.

## 3. Hypotheses
The primary hypothesis concerns iterative execution-verified optimization with diminishing returns under increasing budget. Secondary hypotheses cover iteration, verification, strategy class, budget, model differences, reference proximity, failure modes, and inference cost.

## 4. Related Research Positioning
See research_positioning.md.

## 5. Method
Proposal generation, verification, measurement, and acceptance are distinct components.

## 6. Execution-based Verification
Syntax and objective test execution gate all performance-based decisions.

## 7. Acceptance Strategy
Greedy acceptance is the controlled default. Simulated annealing is an optional search policy over correct candidates.

## 8. Benchmark
Five historical algorithmic tasks are retained with multi-scale deterministic generators.

## 9. Experimental Protocol
Use equal proposal budgets, matched prompts, fixed benchmark revision, fixed hardware/runtime, multiple seeds, warmups, repeats, and preserved raw outputs.

## 10. Baselines
Original, single-shot, iterative, verification-gated, simulated-annealing, and strong manually engineered reference.

## 11. Ablations
A1-A10 as documented in ablations.md.

## 12. Results
Not yet evaluated.

## 13. Failure Analysis
See failure_analysis.md.

## 14. Limitations
Small initial benchmark, visible correctness tests, environment-sensitive timing, and a local executor that is defense in depth rather than a complete sandbox.

## 15. Discussion
Not yet evaluated.

## 16. Reproducibility
See reproducibility.md and REPRODUCIBILITY.md.

## 17. Conclusion
Not yet evaluated. The repository provides the experimental framework, not fabricated empirical conclusions.
