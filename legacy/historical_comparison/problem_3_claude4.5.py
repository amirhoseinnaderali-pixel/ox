def find_duplicate_pairs(nums):
    # O(N) - Group indices by value using a hash map
    value_to_indices = {}
    
    for i, num in enumerate(nums):
        if num not in value_to_indices:
            value_to_indices[num] = []
        value_to_indices[num].append(i)
    
    # O(N) worst case - Generate pairs from grouped indices
    result = []
    for indices in value_to_indices.values():
        # Only process values that appear more than once
        if len(indices) > 1:
            # Generate all pairs (i, j) where i < j
            for i in range(len(indices)):
                for j in range(i + 1, len(indices)):
                    result.append([indices[i], indices[j]])
    
    return result


#####https://claude.ai/share/1aec4491-cff7-470d-a839-dec2fd65f074