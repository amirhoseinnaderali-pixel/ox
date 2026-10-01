#!/usr/bin/env python3
from __future__ import annotations
import argparse,sys
sys.path.insert(0,"src")
from vepo.evaluation.aggregate import aggregate,load_jsonl,write_json
p=argparse.ArgumentParser(); p.add_argument("input"); p.add_argument("--output",required=True); a=p.parse_args()
write_json(a.output,aggregate(load_jsonl(a.input))); print(a.output)
