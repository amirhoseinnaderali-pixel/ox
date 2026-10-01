# Benchmark

The initial suite preserves five historical algorithmic problems. Each metadata file contains a problem definition, correctness cases, a baseline program, a strong manually engineered reference, deterministic input regimes, and expected complexity.

Regimes:
- small: sanity scale
- medium: default controlled scale
- large: primary scalability scale
- stress: optional stress scale

The visible correctness cases are inherited from the historical repository. They are not hidden tests and do not by themselves support broad robustness claims.

A benchmark expansion should add independent test cases, more problem families, and scaling regimes without changing the verification contract.
