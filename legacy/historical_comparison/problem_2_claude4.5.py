def count_subarrays_with_sum(arr, target_sum):
    """
    Count contiguous subarrays with sum equal to target_sum.
    
    Time Complexity: O(N)
    Space Complexity: O(N)
    
    Algorithm:
    - Use prefix sum technique with hash map
    - For each position, check if (prefix_sum - target_sum) exists
    - This means there's a subarray ending at current position with target sum
    """
    count = 0
    prefix_sum = 0
    prefix_map = {0: 1}  # Initialize with 0:1 for subarrays starting at index 0
    
    for num in arr:
        prefix_sum += num
        
        # Check if there's a prefix sum that, when removed, gives target_sum
        # prefix_sum - previous_prefix = target_sum
        # So we need: previous_prefix = prefix_sum - target_sum
        if (prefix_sum - target_sum) in prefix_map:
            count += prefix_map[prefix_sum - target_sum]
        
        # Add current prefix sum to map
        prefix_map[prefix_sum] = prefix_map.get(prefix_sum, 0) + 1
    
    return count


#https://claude.ai/share/bb3a7ec3-fe47-45d0-b82a-2b1095436731