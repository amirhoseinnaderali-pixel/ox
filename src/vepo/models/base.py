from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class Proposal:
    code: str
    strategy: str | None = None
    description: str = ""
    reasoning: str = ""
    estimated_improvement: str | None = None

class ProposalGenerator(Protocol):
    model_name: str
    def propose(self, *, code: str, prompt: str, temperature: float = 0.2) -> Proposal:
        ...
