from pathlib import Path
from vepo.benchmarking.loader import discover_problems

def test_five_historical_problems_are_discoverable():
    problems=discover_problems(Path(__file__).resolve().parents[1]/"benchmarks"/"metadata")
    assert len(problems)==5
    assert {p.problem_id for p in problems}=={"triplets_001","lcs_001","subarray_sum_001","duplicate_pairs_001","matrix_path_001"}
