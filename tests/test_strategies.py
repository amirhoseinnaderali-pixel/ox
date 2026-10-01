from vepo.strategies.catalog import STRATEGIES,strategy_prompt

def test_all_strategies_have_guidance():
    for name in STRATEGIES:
        assert strategy_prompt(name)
