
def longest_common_subsequence(s1, s2):
    """
    Optimized LCS using dynamic programming with space optimization.
    Time: O(m*n), Space: O(min(m,n))
    """
    # Ensure s1 is the shorter string for space optimization
    if len(s1) > len(s2):
        s1, s2 = s2, s1
    
    m, n = len(s1), len(s2)
    
    # Edge cases
    if m == 0 or n == 0:
        return 0
    
    # Use only two rows instead of full 2D table
    prev = [0] * (m + 1)
    curr = [0] * (m + 1)
    
    for j in range(1, n + 1):
        for i in range(1, m + 1):
            if s1[i - 1] == s2[j - 1]:
                curr[i] = prev[i - 1] + 1
            else:
                curr[i] = max(curr[i - 1], prev[i])
        
        # Swap rows
        prev, curr = curr, prev
    
    return prev[m]


# Alternative: Standard DP (easier to understand, slightly more space)
def longest_common_subsequence_standard(s1, s2):
    """
    Standard DP approach.
    Time: O(m*n), Space: O(m*n)
    """
    m, n = len(s1), len(s2)
    
    if m == 0 or n == 0:
        return 0
    
    # Create DP table
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    
    return dp[m][n]
###https://claude.ai/share/9a1bda24-4db2-4325-8e23-52c042d55bfd