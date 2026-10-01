#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
import sys
sys.path.insert(0,"src")
from vepo.benchmarking.loader import discover_problems
from vepo.models.base import Proposal
from vepo.models.mock import StaticProposalModel
from vepo.models.clients import build_client
from vepo.optimizer.engine import OptimizerConfig,optimize
from vepo.verification.executor import ExecutionLimits,PythonExecutor

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--problem",required=True); p.add_argument("--baseline",choices=["single_shot","iterative","verified","simulated_annealing"],default="iterative")
    p.add_argument("--model",default="mock/static"); p.add_argument("--budget",type=int,default=20); p.add_argument("--regime",default="medium"); p.add_argument("--seed",type=int,default=0)
    p.add_argument("--output",required=True); p.add_argument("--timeout",type=float,default=10); p.add_argument("--memory-mb",type=int,default=512)
    a=p.parse_args(); problems=discover_problems("benchmarks/metadata"); problem=next(x for x in problems if x.problem_id==a.problem)
    if a.model=="mock/static": proposer=StaticProposalModel(Proposal(problem.reference_code,strategy="algorithmic",description="historical reference implementation"))
    else: proposer=build_client(a.model)
    policy="simulated_annealing" if a.baseline=="simulated_annealing" else "greedy"
    budget=1 if a.baseline=="single_shot" else a.budget
    cfg=OptimizerConfig(budget=budget,acceptance_policy=policy,input_regime=a.regime,seed=a.seed,baseline_label=a.baseline)
    result=optimize(problem,problem.baseline_code,proposer,PythonExecutor(ExecutionLimits(a.timeout,a.memory_mb)),cfg)
    Path(a.output).parent.mkdir(parents=True,exist_ok=True)
    with open(a.output,"a",encoding="utf-8") as f:
        for r in result.records: f.write(json.dumps(r.to_dict(),sort_keys=True)+"\n")
    print(json.dumps({"output":a.output,"records":len(result.records),"best_code":result.best_code if a.baseline=="single_shot" else None},indent=2))
if __name__=="__main__": main()
