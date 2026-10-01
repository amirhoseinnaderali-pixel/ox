# Reproducibility checklist

Record the repository commit, Python version, OS, CPU and RAM, provider and exact model identifier, benchmark revision, input regime, random seed, warmups, repeats, timeout, memory limit, acceptance policy, and experiment configuration.

Install:
python -m pip install -e '.[test]'

Run tests:
pytest

Run a deterministic smoke benchmark:
python scripts/run_experiment.py --problem subarray_sum_001 --baseline iterative --model mock/static --budget 1 --regime small --seed 42 --output /tmp/vepo-smoke.jsonl

Aggregate:
python scripts/evaluate.py /tmp/vepo-smoke.jsonl --output /tmp/vepo-summary.json

The smoke run validates software plumbing only. It is not a scientific result.
