def longest_common_subsequence(s1: str, s2: str) -> int:
    m, n = len(s1), len(s2)
    
    # Use only two rows to save space
    prev = [0] * (n + 1)
    curr = [0] * (n + 1)
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                curr[j] = prev[j - 1] + 1
            else:
                curr[j] = max(prev[j], curr[j - 1])
        prev, curr = curr, prev
        curr = [0] * (n + 1)  # reset curr (or swap and zero only first element)
    
    return prev[n]

###########https://grok.com/share/c2hhcmQtNA_3d9e89a4-32d5-426b-b46b-5848b6097661