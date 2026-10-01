def count_subarrays_with_sum(arr, target_sum):
    """Return the number of contiguous sub-arrays whose elements sum to *target_sum*.
    O(n) solution using a prefix-sum frequency table.
    """
    freq = {0: 1}
    cur = 0
    cnt = 0
    for num in arr:
        cur += num
        cnt += freq.get(cur - target_sum, 0)
        freq[cur] = freq.get(cur, 0) + 1
    return cnt