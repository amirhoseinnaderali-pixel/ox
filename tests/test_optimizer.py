from vepo.benchmarking.loader import discover_problems
from vepo.models.base import Proposal
from vepo.models.mock import StaticProposalModel
from vepo.optimizer.engine import OptimizerConfig,optimize
from vepo.verification.executor import ExecutionLimits,PythonExecutor

def test_optimizer_keeps_best_while_accepting_can_move_state():
    problem=next(p for p in discover_problems("benchmarks/metadata") if p.problem_id=="subarray_sum_001")
    model=StaticProposalModel(Proposal(problem.reference_code,strategy="algorithmic"))
    result=optimize(problem,problem.baseline_code,model,PythonExecutor(ExecutionLimits(timeout_s=5,memory_mb=512)),
                    OptimizerConfig(budget=2,input_regime="small",seed=42))
    assert result.records[0].correct
    assert any(r.accepted for r in result.records[1:])
    assert result.best_code==problem.reference_code
