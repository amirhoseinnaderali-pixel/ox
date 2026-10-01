from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .generators import GENERATORS
from .schema import ProblemSpec
from vepo.verification.executor import PythonExecutor

@dataclass
class Measurement:
    regime: str
    correctness: dict[str, Any]
    performance: dict[str, Any]

def case_dicts(problem: ProblemSpec) -> list[dict[str, Any]]:
    return [{"function":problem.function_name,"args":c.args,"kwargs":c.kwargs,"expected":c.expected} for c in problem.correctness_cases]

def evaluate_correctness(problem: ProblemSpec, code: str, executor: PythonExecutor) -> dict[str, Any]:
    r=executor.verify(code, case_dicts(problem))
    return {"correct":r.correct,"tests_passed":r.passed,"tests_total":r.total,"errors":r.errors,"failure_type":r.failure_type}

def evaluate_performance(problem: ProblemSpec, code: str, executor: PythonExecutor, regime: str, *, seed: int|None=None, correctness: dict[str,Any]|None=None) -> Measurement:
    spec=next(x for x in problem.regimes if x.name==regime)
    payload=GENERATORS[problem.generator_name](regime, spec.seed if seed is None else seed)
    correctness = correctness if correctness is not None else evaluate_correctness(problem,code,executor)
    r=executor.benchmark(code,problem.function_name,payload["args"],payload["kwargs"],warmups=spec.warmups,repeats=spec.repeats)
    return Measurement(regime,correctness,{"runtime_ms":r.runtime_ms,"runtime_std_ms":r.runtime_std_ms,"memory_mb":r.memory_mb,"error":r.error,"failure_type":r.failure_type})
