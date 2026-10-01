def find_triplets_sum_zero(arr):
    n = len(arr)
    if n < 3:
        return []
    arr.sort()
    result = []
    append_res = result.append
    i = 0
    while i < n - 2:
        a = arr[i]
        if a > 0:
            break
        if i > 0 and a == arr[i - 1]:
            i += 1
            continue
        left = i + 1
        right = n - 1
        while left < right:
            b = arr[left]
            c = arr[right]
            total = a + b + c
            if total == 0:
                append_res([a, b, c])
                # skip duplicates for b
                while left < right and arr[left] == b:
                    left += 1
                # skip duplicates for c
                while left < right and arr[right] == c:
                    right -= 1
            elif total < 0:
                left += 1
            else:
                right -= 1
        i += 1
    return result