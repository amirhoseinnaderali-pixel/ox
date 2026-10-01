from __future__ import annotations
from dataclasses import asdict, dataclass, field
from typing import Any

@dataclass(frozen=True)
class CorrectnessCase:
    case_id: str
    args: list[Any] = field(default_factory=list)
    kwargs: dict[str, Any] = field(default_factory=dict)
    expected: Any = None

@dataclass(frozen=True)
class BenchmarkRegime:
    name: str
    repeats: int = 10
    warmups: int = 3
    seed: int = 0
    description: str = ""

@dataclass(frozen=True)
class ProblemSpec:
    problem_id: str
    title: str
    category: str
    difficulty: str
    description: str
    function_name: str
    constraints: str
    baseline_code: str
    reference_code: str
    correctness_cases: tuple[CorrectnessCase, ...]
    regimes: tuple[BenchmarkRegime, ...]
    generator_name: str | None = None
    expected_complexity: str | None = None

    def to_metadata(self) -> dict[str, Any]:
        return asdict(self)
