#!/usr/bin/env python3
from __future__ import annotations
import argparse,sys
sys.path.insert(0,"src")
from vepo.evaluation.aggregate import aggregate,load_jsonl,write_json
p=argparse.ArgumentParser(); p.add_argument("inputs",nargs="+"); p.add_argument("--output",required=True); a=p.parse_args()
rows=[]
for path in a.inputs: rows.extend(load_jsonl(path))
write_json(a.output,aggregate(rows)); print(a.output)
