def find_triplets_sum_zero(arr):
    arr.sort()                    # Sort once: O(N log N)
    result = []
    n = len(arr)
    
    for i in range(n - 2):
        # Skip duplicate values for i (avoid duplicate triplets)
        if i > 0 and arr[i] == arr[i - 1]:
            continue
            
        # Two pointers for the remaining part
        left = i + 1
        right = n - 1
        
        while left < right:
            total = arr[i] + arr[left] + arr[right]
            
            if total == 0:
                result.append([arr[i], arr[left], arr[right]])
                
                # Skip duplicates for left
                while left < right and arr[left] == arr[left + 1]:
                    left += 1
                # Skip duplicates for right
                while left < right and arr[right] == arr[right - 1]:
                    right -= 1
                    
                left += 1
                right -= 1
                
            elif total < 0:
                left += 1
            else:
                right -= 1
                
    return result



###########https://grok.com/share/c2hhcmQtNA_3d9e89a4-32d5-426b-b46b-5848b6097661