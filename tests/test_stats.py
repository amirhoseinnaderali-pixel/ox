from vepo.evaluation.stats import bootstrap_mean_ci

def test_bootstrap_ci_is_reproducible():
    assert bootstrap_mean_ci([1,2,3,4],seed=7)==bootstrap_mean_ci([1,2,3,4],seed=7)
