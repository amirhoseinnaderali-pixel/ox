from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from .schema import BenchmarkRegime, CorrectnessCase, ProblemSpec

def load_metadata(path: str | Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_problem(path: str | Path) -> ProblemSpec:
    raw = load_metadata(path)
    return ProblemSpec(
        problem_id=raw["problem_id"], title=raw["title"], category=raw["category"],
        difficulty=raw["difficulty"], description=raw["description"],
        function_name=raw["function_name"], constraints=raw["constraints"],
        baseline_code=raw["baseline_code"], reference_code=raw["reference_code"],
        correctness_cases=tuple(CorrectnessCase(**x) for x in raw["correctness_cases"]),
        regimes=tuple(BenchmarkRegime(**x) for x in raw["regimes"]),
        generator_name=raw.get("generator_name"), expected_complexity=raw.get("expected_complexity"),
    )

def discover_problems(metadata_dir: str | Path) -> list[ProblemSpec]:
    return [load_problem(p) for p in sorted(Path(metadata_dir).glob("*.json"))]
