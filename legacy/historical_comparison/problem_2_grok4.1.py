from collections import defaultdict
from typing import List

def count_subarrays_with_sum(arr: List[int], target_sum: int) -> int:
    """
    Count contiguous subarrays whose sum equals target_sum.
    
    Time  : O(N)
    Space : O(N)
    """
    prefix_to_count = defaultdict(int)
    prefix_to_count[0] = 1          # one way to get sum = 0 (empty subarray before index 0)
    
    current_sum = 0
    count = 0
    
    for num in arr:
        current_sum += num
        
        # If (current_sum - target_sum) has been seen before,
        # all those positions start a subarray that ends here and sums to target_sum
        if current_sum - target_sum in prefix_to_count:
            count += prefix_to_count[current_sum - target_sum]
        
        # Record the current prefix sum
        prefix_to_count[current_sum] += 1
    
    return count

##########https://grok.com/share/c2hhcmQtNA_75021f86-0c4e-453c-957d-082323c2e121