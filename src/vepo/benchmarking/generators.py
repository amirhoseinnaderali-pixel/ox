from __future__ import annotations
import random, string
from typing import Any

SIZES = {
    "triplets": {"small": 64, "medium": 512, "large": 3000, "stress": 6000},
    "lcs": {"small": 64, "medium": 256, "large": 1024, "stress": 2048},
    "subarray_sum": {"small": 128, "medium": 2000, "large": 20000, "stress": 100000},
    "duplicate_pairs": {"small": 128, "medium": 2000, "large": 5000, "stress": 10000},
    "matrix_path": {"small": 16, "medium": 64, "large": 128, "stress": 256},
}

def triplets(regime: str, seed: int) -> dict[str, Any]:
    rng=random.Random(seed); n=SIZES["triplets"][regime]
    arr=[rng.randint(-100000,100000) for _ in range(n)]
    return {"args":[arr],"kwargs":{}}

def lcs(regime: str, seed: int) -> dict[str, Any]:
    rng=random.Random(seed); n=SIZES["lcs"][regime]; a=string.ascii_uppercase[:8]
    return {"args":["".join(rng.choices(a,k=n)),"".join(rng.choices(a,k=n))],"kwargs":{}}

def subarray_sum(regime: str, seed: int) -> dict[str, Any]:
    rng=random.Random(seed); n=SIZES["subarray_sum"][regime]
    return {"args":[[rng.randint(-20,20) for _ in range(n)],7],"kwargs":{}}

def duplicate_pairs(regime: str, seed: int) -> dict[str, Any]:
    rng=random.Random(seed); n=SIZES["duplicate_pairs"][regime]
    return {"args":[[rng.randint(0,max(2,n//4)) for _ in range(n)]],"kwargs":{}}

def matrix_path(regime: str, seed: int) -> dict[str, Any]:
    rng=random.Random(seed); side=SIZES["matrix_path"][regime]
    return {"args":[[rng.randint(-20,20) for _ in range(side)] for _ in range(side)],"kwargs":{}}

GENERATORS={"triplets":triplets,"lcs":lcs,"subarray_sum":subarray_sum,"duplicate_pairs":duplicate_pairs,"matrix_path":matrix_path}
