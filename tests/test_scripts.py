import json, subprocess, sys

def test_cli_smoke(tmp_path):
    out=tmp_path/"run.jsonl"
    cmd=[sys.executable,"scripts/run_experiment.py","--problem","subarray_sum_001","--baseline","iterative","--model","mock/static","--budget","1","--regime","small","--seed","42","--output",str(out)]
    r=subprocess.run(cmd,capture_output=True,text=True)
    assert r.returncode==0, r.stderr
    assert len(out.read_text().splitlines())==2
    assert json.loads(out.read_text().splitlines()[1])["correct"] is True
