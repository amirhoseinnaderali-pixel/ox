from __future__ import annotations
from .base import Proposal

class StaticProposalModel:
    """Deterministic proposal generator for smoke tests and CI."""
    model_name = "mock/static"
    def __init__(self, proposal: Proposal):
        self.proposal = proposal
        self.calls = 0
    def propose(self, *, code: str, prompt: str, temperature: float = 0.2) -> Proposal:
        self.calls += 1
        return self.proposal
