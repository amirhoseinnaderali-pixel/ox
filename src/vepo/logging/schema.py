from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

SCHEMA_VERSION = "1.0"

@dataclass
class RunRecord:
    experiment_id: str
    problem_id: str
    model: str
    baseline: str
    seed: int
    budget: int
    iteration: int
    correct: bool
    tests_passed: int
    tests_total: int
    runtime_ms: float | None
    memory_mb: float | None
    accepted: bool
    strategy: str | None
    model_calls: int
    latency_s: float | None
    failure_type: str | None
    acceptance_reason: str | None = None
    warmups: int | None = None
    repeats: int | None = None
    input_regime: str | None = None
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["schema_version"] = SCHEMA_VERSION
        return result
