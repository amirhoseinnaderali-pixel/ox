#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys, time
from pathlib import Path
sys.path.insert(0,"src")
from vepo.benchmarking.loader import discover_problems
from vepo.benchmarking.runner import evaluate_correctness, evaluate_performance
from vepo.logging.schema import RunRecord
from vepo.models.base import Proposal
from vepo.models.clients import build_client
from vepo.models.mock import StaticProposalModel
from vepo.optimizer.engine import OptimizerConfig, optimize
from vepo.verification.executor import ExecutionLimits, PythonExecutor

def record_static(problem, code, label, model, seed, regime, executor):
    corr=evaluate_correctness(problem,code,executor)
    perf=evaluate_performance(problem,code,executor,regime,seed=seed,correctness=corr)
    spec=next(x for x in problem.regimes if x.name==regime)
    return RunRecord(
        experiment_id=f"{problem.problem_id}-{label}-{seed}", problem_id=problem.problem_id, model=model,
        baseline=label, seed=seed, budget=0, iteration=0, correct=corr["correct"],
        tests_passed=corr["tests_passed"], tests_total=corr["tests_total"], runtime_ms=perf.performance["runtime_ms"],
        memory_mb=perf.performance["memory_mb"], accepted=True, strategy=None, model_calls=0, latency_s=0.0,
        failure_type=corr["failure_type"] or perf.performance["failure_type"], acceptance_reason="static_baseline",
        warmups=spec.warmups, repeats=spec.repeats, input_regime=regime)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--problem",required=True)
    ap.add_argument("--baseline",choices=["original","reference","single_shot","iterative","verified","simulated_annealing"],default="iterative")
    ap.add_argument("--model",default="mock/static")
    ap.add_argument("--budget",type=int,default=20)
    ap.add_argument("--regime",default="medium")
    ap.add_argument("--seed",type=int,default=0)
    ap.add_argument("--output",required=True)
    ap.add_argument("--timeout",type=float,default=10)
    ap.add_argument("--memory-mb",type=int,default=512)
    a=ap.parse_args()
    problem=next(x for x in discover_problems("benchmarks/metadata") if x.problem_id==a.problem)
    executor=PythonExecutor(ExecutionLimits(a.timeout,a.memory_mb))
    if a.baseline in {"original","reference"}:
        code=problem.baseline_code if a.baseline=="original" else problem.reference_code
        rows=[record_static(problem,code,a.baseline,a.model,a.seed,a.regime,executor)]
        best_code=code
    else:
        if a.model=="mock/static":
            proposer=StaticProposalModel(Proposal(problem.reference_code,strategy="algorithmic",description="manually engineered reference"))
        else:
            proposer=build_client(a.model)
        policy="simulated_annealing" if a.baseline=="simulated_annealing" else "greedy"
        budget=1 if a.baseline=="single_shot" else a.budget
        result=optimize(problem,problem.baseline_code,proposer,executor,
                         OptimizerConfig(budget=budget,acceptance_policy=policy,input_regime=a.regime,seed=a.seed,baseline_label=a.baseline))
        rows=result.records; best_code=result.best_code
    out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("a",encoding="utf-8") as f:
        for row in rows: f.write(json.dumps(row.to_dict(),sort_keys=True)+"\n")
    print(json.dumps({"output":str(out),"records":len(rows),"best_code":best_code if a.baseline not in {"original","reference"} else None},indent=2))

if __name__=="__main__":
    main()
