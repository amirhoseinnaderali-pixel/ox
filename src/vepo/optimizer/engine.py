from __future__ import annotations
import random, time
from dataclasses import dataclass, field
from typing import Any
from vepo.acceptance.policies import correctness_gated
from vepo.benchmarking.runner import evaluate_correctness, evaluate_performance
from vepo.benchmarking.schema import ProblemSpec
from vepo.logging.schema import RunRecord
from vepo.models.base import Proposal, ProposalGenerator
from vepo.strategies.catalog import STRATEGIES, strategy_prompt
from vepo.verification.executor import PythonExecutor

@dataclass
class OptimizerConfig:
    budget:int=20
    acceptance_policy:str="greedy"
    strategy:str|None=None
    input_regime:str="medium"
    seed:int=0
    temperature_initial:float=0.5
    temperature_final:float=0.02
    baseline_label:str="iterative"

@dataclass
class OptimizationResult:
    best_code:str
    records:list[RunRecord]=field(default_factory=list)

def _temperature(i:int,budget:int,initial:float,final:float)->float:
    if budget<=1: return final
    return initial+(final-initial)*(i-1)/(budget-1)

def build_prompt(problem:ProblemSpec,code:str,iteration:int,strategy:str|None,history:list[dict[str,Any]])->str:
    guide=strategy_prompt(strategy) if strategy else "Use the most evidence-based optimization available."
    return f"""You are optimizing executable Python under a fixed proposal budget.
Problem: {problem.title} ({problem.problem_id})
Correctness is a hard constraint: a candidate with changed outputs must never be accepted.
Iteration: {iteration}
Strategy: {strategy or 'adaptive'}
Guidance: {guide}
Current program:
<python>
{code}
</python>
Return JSON with code, strategy, description, reasoning, estimated_improvement.
Return a complete program, not a diff.
Recent history: {history[-3:]}
"""

def optimize(problem:ProblemSpec,initial_code:str,proposer:ProposalGenerator,executor:PythonExecutor,config:OptimizerConfig)->OptimizationResult:
    rng=random.Random(config.seed)
    current_code=initial_code
    records=[]
    history=[]
    experiment_id=f"{problem.problem_id}-{config.seed}-{config.budget}-{config.acceptance_policy}"
    baseline_correctness=evaluate_correctness(problem,current_code,executor)
    baseline=evaluate_performance(problem,current_code,executor,config.input_regime,seed=config.seed,correctness=baseline_correctness)
    current_runtime=baseline.performance["runtime_ms"] if baseline_correctness["correct"] else None
    best_runtime=current_runtime
    best_code=initial_code
    model_calls=0
    start=time.perf_counter()
    records.append(RunRecord(experiment_id,problem.problem_id,proposer.model_name,config.baseline_label,config.seed,config.budget,0,
        baseline_correctness["correct"],baseline_correctness["tests_passed"],baseline_correctness["tests_total"],
        baseline.performance["runtime_ms"],baseline.performance["memory_mb"],True,None,0,0.0,
        baseline_correctness["failure_type"] or baseline.performance["failure_type"],"initial_program",
        input_regime=config.input_regime))
    for iteration in range(1,config.budget+1):
        strategy=config.strategy or list(STRATEGIES)[(iteration-1)%len(STRATEGIES)]
        prompt=build_prompt(problem,current_code,iteration,strategy,history)
        t0=time.perf_counter()
        try:
            proposal=proposer.propose(code=current_code,prompt=prompt,temperature=0.2); call_error=None
        except Exception as exc:
            proposal=Proposal(code="",strategy=strategy); call_error=f"{type(exc).__name__}: {exc}"
        latency=time.perf_counter()-t0; model_calls+=1
        correctness=evaluate_correctness(problem,proposal.code,executor) if proposal.code else {
            "correct":False,"tests_passed":0,"tests_total":len(problem.correctness_cases),
            "errors":[call_error or "empty proposal"],"failure_type":"serialization/parsing_failure"}
        perf=evaluate_performance(problem,proposal.code,executor,config.input_regime,seed=config.seed,correctness=correctness) if correctness["correct"] else None
        candidate_runtime=perf.performance["runtime_ms"] if perf else None
        decision=correctness_gated(correct=correctness["correct"],
            current_runtime_ms=current_runtime if current_runtime is not None else float("inf"),
            candidate_runtime_ms=candidate_runtime if candidate_runtime is not None else float("inf"),
            policy=config.acceptance_policy,temperature=_temperature(iteration,config.budget,config.temperature_initial,config.temperature_final),rng=rng)
        if decision.accepted:
            current_code=proposal.code
            current_runtime=candidate_runtime
            if candidate_runtime is not None and (best_runtime is None or candidate_runtime<best_runtime):
                best_code=proposal.code; best_runtime=candidate_runtime
        rec=RunRecord(experiment_id,problem.problem_id,proposer.model_name,config.baseline_label,config.seed,config.budget,iteration,
            correctness["correct"],correctness["tests_passed"],correctness["tests_total"],candidate_runtime,
            perf.performance["memory_mb"] if perf else None,decision.accepted,proposal.strategy or strategy,model_calls,latency,
            correctness["failure_type"] or (perf.performance["failure_type"] if perf else None),decision.reason,
            warmups=next(x.warmups for x in problem.regimes if x.name==config.input_regime),
            repeats=next(x.repeats for x in problem.regimes if x.name==config.input_regime),
            input_regime=config.input_regime)
        records.append(rec)
        history.append({"iteration":iteration,"correct":rec.correct,"runtime_ms":rec.runtime_ms,"accepted":rec.accepted,"failure_type":rec.failure_type})
    elapsed=time.perf_counter()-start
    for r in records: r.metadata={"wall_clock_s":elapsed}
    return OptimizationResult(best_code,records)
