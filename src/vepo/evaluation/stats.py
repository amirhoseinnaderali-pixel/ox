from __future__ import annotations
import random
from statistics import mean

def bootstrap_mean_ci(values:list[float],seed:int=0,n_resamples:int=2000,alpha:float=0.05)->tuple[float,float]|None:
    if not values: return None
    rng=random.Random(seed); n=len(values); means=[]
    for _ in range(n_resamples):
        sample=[values[rng.randrange(n)] for _ in range(n)]
        means.append(mean(sample))
    means.sort()
    lo=means[int((alpha/2)*n_resamples)]
    hi=means[int((1-alpha/2)*n_resamples)-1]
    return lo,hi
