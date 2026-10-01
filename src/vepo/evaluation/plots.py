from __future__ import annotations
from pathlib import Path
import matplotlib.pyplot as plt

def plot_runtime_by_iteration(rows:list[dict],out:str|Path)->None:
    xs=[r["iteration"] for r in rows if r.get("runtime_ms") is not None]
    ys=[r["runtime_ms"] for r in rows if r.get("runtime_ms") is not None]
    fig,ax=plt.subplots(figsize=(7,4)); ax.plot(xs,ys,marker="o"); ax.set_xlabel("Iteration"); ax.set_ylabel("Median runtime (ms)")
    ax.set_title("Runtime vs optimization iteration"); fig.tight_layout(); Path(out).parent.mkdir(parents=True,exist_ok=True); fig.savefig(out,dpi=160); plt.close(fig)
