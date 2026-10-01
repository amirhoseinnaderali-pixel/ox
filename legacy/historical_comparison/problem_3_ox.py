def find_duplicate_pairs(nums):
    # O(N^2) brute force comparison
    result = []
    n = len(nums)
    
    for i in range(n):
        for j in range(i + 1, n):
            if nums[i] == nums[j]:
                result.append([i, j])
    
    return result



    