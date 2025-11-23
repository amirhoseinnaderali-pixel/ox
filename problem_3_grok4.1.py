from collections import defaultdict
from itertools import combinations

def find_duplicate_pairs(nums):
    pos = defaultdict(list)
    for i, num in enumerate(nums):
        pos[num].append(i)
    
    return [list(pair) for pair in 
            sorted(combinations(idx, 2) for indices in pos.values() 
                   for idx in [sorted(indices)] if len(idx) >= 2)]
#######https://grok.com/share/c2hhcmQtNA_8289bf2a-1515-4809-b2f7-e6d772b75558