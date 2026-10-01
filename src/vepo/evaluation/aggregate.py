from __future__ import annotations
import json, statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

def load_jsonl(path:str|Path)->list[dict[str,Any]]:
    return [json.loads(x) for x in Path(path).read_text(encoding="utf-8").splitlines() if x.strip()]

def aggregate(rows:list[dict[str,Any]])->list[dict[str,Any]]:
    groups=defaultdict(list)
    for r in rows: groups[(r["problem_id"],r["model"],r["baseline"],r.get("input_regime"))].append(r)
    out=[]
    for key,items in groups.items():
        runtimes=[r["runtime_ms"] for r in items if r.get("runtime_ms") is not None and r.get("correct")]
        correct=sum(bool(r.get("correct")) for r in items)
        accepted=sum(bool(r.get("accepted")) for r in items[1:])
        out.append({"problem_id":key[0],"model":key[1],"baseline":key[2],"input_regime":key[3],
                     "records":len(items),"correctness_rate":correct/len(items) if items else None,
                     "median_runtime_ms":statistics.median(runtimes) if runtimes else None,
                     "runtime_samples":len(runtimes),"accepted_proposals":accepted})
    return sorted(out,key=lambda x:(x["problem_id"],x["baseline"],x["input_regime"] or ""))

def write_json(path:str|Path,data:Any)->None:
    Path(path).write_text(json.dumps(data,indent=2),encoding="utf-8")
