from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import requests
from .base import Proposal

@dataclass
class OllamaClient:
    model_name: str
    base_url: str = "http://localhost:11434"

    def propose(self, *, code: str, prompt: str, temperature: float = 0.2) -> Proposal:
        response = requests.post(
            f"{self.base_url.rstrip('/')}/api/generate",
            json={"model": self.model_name, "prompt": prompt, "stream": False, "options": {"temperature": temperature}},
            timeout=(15, 300),
        )
        response.raise_for_status()
        payload: dict[str, Any] = response.json()
        return parse_proposal(payload.get("response", ""))

def parse_proposal(raw: str) -> Proposal:
    text = raw.strip()
    marker = chr(96) * 3
    if text.startswith(marker):
        text = text.strip(marker)
        if text.startswith("json"):
            text = text[4:].strip()
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("LLM response does not contain a JSON object")
    payload = json.loads(text[start:end+1])
    code = payload.get("code")
    if not isinstance(code, str) or not code.strip():
        raise ValueError("LLM response is missing a non-empty 'code' field")
    return Proposal(code=code, strategy=payload.get("strategy") or payload.get("description"),
                    description=payload.get("description", ""), reasoning=payload.get("reasoning", ""),
                    estimated_improvement=payload.get("estimated_improvement"))

def build_client(model_name: str):
    if model_name.startswith("ollama/"):
        return OllamaClient(model_name=model_name.split("/", 1)[1])
    raise ValueError("Only ollama/<model> is configured for live network proposals; use mock/static in CI.")
