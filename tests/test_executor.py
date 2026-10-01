from vepo.verification.executor import ExecutionLimits,PythonExecutor

def test_executor_verifies_correct_candidate():
    r=PythonExecutor(ExecutionLimits(timeout_s=5,memory_mb=512)).verify("def f(x):\n    return x+1\n",[{"function":"f","args":[1],"kwargs":{},"expected":2}])
    assert r.correct and r.passed==1

def test_executor_rejects_wrong_output():
    r=PythonExecutor(ExecutionLimits(timeout_s=5,memory_mb=512)).verify("def f(x):\n    return x-1\n",[{"function":"f","args":[1],"kwargs":{},"expected":2}])
    assert not r.correct and r.failure_type=="incorrect_output"
