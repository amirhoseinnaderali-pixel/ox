from __future__ import annotations

from dataclasses import dataclass
import math
import random

@dataclass(frozen=True)
class AcceptanceDecision:
    accepted: bool
    reason: str
    probability: float = 0.0

def greedy_accept(current_runtime_ms: float, candidate_runtime_ms: float) -> AcceptanceDecision:
    if candidate_runtime_ms < current_runtime_ms:
        return AcceptanceDecision(True, "lower_runtime", 1.0)
    return AcceptanceDecision(False, "not_faster", 0.0)

def simulated_annealing_accept(current_runtime_ms: float, candidate_runtime_ms: float, temperature: float, rng: random.Random) -> AcceptanceDecision:
    if candidate_runtime_ms < current_runtime_ms:
        return AcceptanceDecision(True, "lower_runtime", 1.0)
    if temperature <= 0:
        return AcceptanceDecision(False, "non_improving_at_zero_temperature", 0.0)
    if not math.isfinite(candidate_runtime_ms) or not math.isfinite(current_runtime_ms):
        return AcceptanceDecision(False, "non_finite_runtime", 0.0)
    delta = (candidate_runtime_ms - current_runtime_ms) / max(current_runtime_ms, 1e-9)
    probability = math.exp(-delta / temperature)
    accepted = rng.random() < probability
    return AcceptanceDecision(accepted, "annealed_acceptance" if accepted else "annealed_rejection", probability)

def correctness_gated(*, correct: bool, current_runtime_ms: float, candidate_runtime_ms: float, policy: str, temperature: float = 0.0, rng: random.Random | None = None) -> AcceptanceDecision:
    if not correct:
        return AcceptanceDecision(False, "correctness_failed", 0.0)
    if policy == "greedy":
        return greedy_accept(current_runtime_ms, candidate_runtime_ms)
    if policy == "simulated_annealing":
        return simulated_annealing_accept(current_runtime_ms, candidate_runtime_ms, temperature, rng or random.Random(0))
    raise ValueError(f"Unknown acceptance policy: {policy}")
