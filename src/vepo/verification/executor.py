from __future__ import annotations

import base64
import json
import os
import resource
import subprocess
import sys
import tempfile
import textwrap
import time
from dataclasses import dataclass
from typing import Any

from .verifier import classify_failure, validate_syntax

@dataclass(frozen=True)
class ExecutionLimits:
    timeout_s: float = 10.0
    memory_mb: int = 512
    max_output_bytes: int = 1_000_000

@dataclass
class CorrectnessResult:
    correct: bool
    passed: int
    total: int
    errors: list[str]
    failure_type: str | None
    wall_time_s: float | None

@dataclass
class PerformanceResult:
    runtime_ms: float | None
    runtime_std_ms: float | None
    memory_mb: float | None
    error: str | None = None
    failure_type: str | None = None

class PythonExecutor:
    """Best-effort restricted executor; not a security boundary."""
    def __init__(self, limits: ExecutionLimits):
        self.limits = limits

    def _preexec(self):
        if os.name != "posix": return
        cpu = max(1, int(self.limits.timeout_s))
        memory = self.limits.memory_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu))
        if hasattr(resource, "RLIMIT_DATA"):
            resource.setrlimit(resource.RLIMIT_DATA, (memory, memory))
        resource.setrlimit(resource.RLIMIT_FSIZE, (self.limits.max_output_bytes, self.limits.max_output_bytes))
        if hasattr(resource, "RLIMIT_NOFILE"):
            resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))

    def _run(self, script: str) -> tuple[int, str, str, float]:
        with tempfile.TemporaryDirectory(prefix="vepo-exec-") as td:
            path = os.path.join(td, "runner.py")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(script)
            env = {"PATH": os.environ.get("PATH", ""), "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED", "0")}
            started = time.perf_counter()
            try:
                result = subprocess.run([sys.executable, "-I", path], cwd=td, env=env,
                                        capture_output=True, text=True,
                                        timeout=self.limits.timeout_s + 1.0,
                                        preexec_fn=self._preexec if os.name == "posix" else None)
            except subprocess.TimeoutExpired:
                return 124, "", "timeout", time.perf_counter() - started
            return result.returncode, result.stdout[-self.limits.max_output_bytes:], result.stderr[-self.limits.max_output_bytes:], time.perf_counter() - started

    def verify(self, code: str, cases: list[dict[str, Any]]) -> CorrectnessResult:
        syntax = validate_syntax(code)
        if not syntax.valid:
            return CorrectnessResult(False, 0, len(cases), [syntax.error or "syntax error"], "syntax_failure", None)
        payload = base64.b64encode(json.dumps(cases).encode()).decode()
        script = textwrap.dedent(f"""
            import base64, json, time
            CODE = {code!r}
            CASES = json.loads(base64.b64decode({payload!r}).decode())
            ns={{}}; started=time.perf_counter(); errors=[]; passed=0
            try:
                exec(compile(CODE, '<candidate>', 'exec'), ns, ns)
                for idx, case in enumerate(CASES):
                    try:
                        actual=ns[case['function']](*case.get('args', []), **case.get('kwargs', {{}}))
                        if actual == case.get('expected'): passed += 1
                        else: errors.append(f"case={{idx}} expected={{case.get('expected')!r}} got={{actual!r}}")
                    except Exception as exc:
                        errors.append(f"case={{idx}} {{type(exc).__name__}}: {{exc}}")
            except Exception as exc:
                errors.append(f"load {{type(exc).__name__}}: {{exc}}")
            print(json.dumps({{'passed':passed,'total':len(CASES),'errors':errors,'wall_time_s':time.perf_counter()-started}}))
        """)
        returncode, stdout, stderr, _ = self._run(script)
        if returncode == 124:
            return CorrectnessResult(False, 0, len(cases), ["execution timeout"], "timeout", None)
        try:
            result = json.loads(stdout.splitlines()[-1])
        except Exception:
            return CorrectnessResult(False, 0, len(cases), [stderr or stdout or "unparseable executor output"], "serialization/parsing_failure", None)
        passed, total, errors = int(result.get("passed", 0)), int(result.get("total", len(cases))), list(result.get("errors", []))
        failure = None if passed == total else "incorrect_output"
        if returncode != 0 and not failure:
            failure = classify_failure(runtime_error=stderr or "non-zero exit")
        return CorrectnessResult(passed == total and not failure, passed, total, errors, failure, result.get("wall_time_s"))

    def benchmark(self, code: str, function_name: str, args: list[Any], kwargs: dict[str, Any], *, warmups: int, repeats: int) -> PerformanceResult:
        syntax = validate_syntax(code)
        if not syntax.valid:
            return PerformanceResult(None, None, None, syntax.error, "syntax_failure")
        payload = base64.b64encode(json.dumps({"args": args, "kwargs": kwargs}).encode()).decode()
        script = textwrap.dedent(f"""
            import base64, json, os, statistics, time, tracemalloc, resource
            CODE={code!r}
            PAYLOAD=json.loads(base64.b64decode({payload!r}).decode())
            ns={{}}; exec(compile(CODE, '<candidate>', 'exec'), ns, ns)
            fn=ns[{function_name!r}]; args=PAYLOAD['args']; kwargs=PAYLOAD['kwargs']
            for _ in range({warmups}): fn(*args, **kwargs)
            times=[]; tracemalloc.start()
            for _ in range({repeats}):
                t0=time.perf_counter_ns(); fn(*args, **kwargs); t1=time.perf_counter_ns()
                times.append((t1-t0)/1_000_000.0)
            current, peak=tracemalloc.get_traced_memory(); tracemalloc.stop()
            rss=getattr(resource.getrusage(resource.RUSAGE_SELF), 'ru_maxrss', 0)
            print(json.dumps({{'median_ms':statistics.median(times),'stdev_ms':statistics.pstdev(times) if len(times)>1 else 0.0,'memory_mb_tracemalloc':peak/1024/1024,'max_rss_raw':rss,'platform':os.name}}))
        """)
        returncode, stdout, stderr, _ = self._run(script)
        if returncode == 124:
            return PerformanceResult(None, None, None, "execution timeout", "timeout")
        if returncode != 0:
            return PerformanceResult(None, None, None, stderr[-2000:], "memory_failure" if "MemoryError" in stderr else "runtime_failure")
        try:
            result = json.loads(stdout.splitlines()[-1])
        except Exception:
            return PerformanceResult(None, None, None, "unparseable benchmark output", "serialization/parsing_failure")
        return PerformanceResult(float(result["median_ms"]), float(result["stdev_ms"]), float(result["memory_mb_tracemalloc"]))
