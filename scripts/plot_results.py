#!/usr/bin/env python3
from __future__ import annotations
import argparse,sys
sys.path.insert(0,"src")
from vepo.evaluation.aggregate import load_jsonl
from vepo.evaluation.plots import plot_runtime_by_iteration
p=argparse.ArgumentParser(); p.add_argument("input"); p.add_argument("--output",required=True); a=p.parse_args()
plot_runtime_by_iteration(load_jsonl(a.input),a.output)
