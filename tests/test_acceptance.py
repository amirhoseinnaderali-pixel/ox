import random
from vepo.acceptance.policies import correctness_gated

def test_incorrect_candidate_is_never_accepted():
    d=correctness_gated(correct=False,current_runtime_ms=10,candidate_runtime_ms=1,policy="simulated_annealing",temperature=1,rng=random.Random(0))
    assert not d.accepted
    assert d.reason=="correctness_failed"

def test_greedy_accepts_lower_runtime():
    d=correctness_gated(correct=True,current_runtime_ms=10,candidate_runtime_ms=9,policy="greedy")
    assert d.accepted
