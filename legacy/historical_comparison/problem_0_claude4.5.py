def find_triplets_sum_zero(arr):
    """
    Find all unique triplets that sum to zero using two-pointer approach.
    Time Complexity: O(N^2)
    Space Complexity: O(1) excluding output
    """
    # Sort the array first - O(N log N)
    arr.sort()
    result = []
    n = len(arr)
    
    # Iterate through array, fixing one element at a time
    for i in range(n - 2):
        # Skip duplicate values for first element
        if i > 0 and arr[i] == arr[i - 1]:
            continue
        
        # Early termination: if smallest element is positive, no triplet possible
        if arr[i] > 0:
            break
        
        # Two-pointer approach for remaining elements
        left = i + 1
        right = n - 1
        target = -arr[i]
        
        while left < right:
            current_sum = arr[left] + arr[right]
            
            if current_sum == target:
                result.append([arr[i], arr[left], arr[right]])
                
                # Skip duplicates for second element
                while left < right and arr[left] == arr[left + 1]:
                    left += 1
                # Skip duplicates for third element
                while left < right and arr[right] == arr[right - 1]:
                    right -= 1
                
                left += 1
                right -= 1
            elif current_sum < target:
                left += 1
            else:
                right -= 1
    
    return result



#######https://claude.ai/share/cff78641-1998-41d4-bd78-e2dcdbabcb52