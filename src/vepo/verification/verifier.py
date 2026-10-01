from __future__ import annotations
import ast
from dataclasses import dataclass

@dataclass(frozen=True)
class SyntaxValidation:
    valid: bool
    error: str | None = None

def validate_syntax(code: str) -> SyntaxValidation:
    try:
        ast.parse(code)
    except SyntaxError as exc:
        return SyntaxValidation(False, f"{exc.__class__.__name__}: {exc}")
    return SyntaxValidation(True, None)

def classify_failure(*, syntax_error: str | None = None, runtime_error: str | None = None,
                     timeout: bool = False, memory_error: bool = False,
                     incorrect_output: bool = False, parser_error: bool = False) -> str | None:
    if parser_error: return "serialization/parsing_failure"
    if syntax_error: return "syntax_failure"
    if timeout: return "timeout"
    if memory_error: return "memory_failure"
    if runtime_error: return "runtime_failure"
    if incorrect_output: return "incorrect_output"
    return None
