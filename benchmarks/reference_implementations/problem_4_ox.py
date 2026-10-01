from itertools import accumulate

def matrix_max_path_sum(matrix):
    """Return the maximum sum from top‑left to bottom‑right moving only down or right.
    Runs in O(m·n) time and O(n) extra space.
    """
    if not matrix or not matrix[0]:
        return 0

    m, n = len(matrix), len(matrix[0])

    # trivial dimensions – early return
    if m == 1:
        return sum(matrix[0])
    if n == 1:
        return sum(row[0] for row in matrix)
    if m == 2 and n == 2:
        a, b = matrix[0]
        c, d = matrix[1]
        # max path: a -> (b or c) -> d
        return a + d + (b if b > c else c)

    # first row cumulative sums using C‑level accumulate
    dp = list(accumulate(matrix[0]))

    _max = max  # local bind for speed
    for i in range(1, m):
        row = matrix[i]
        # first column can only come from above
        dp0 = dp[0] + row[0]
        dp[0] = dp0
        left = dp0
        for j in range(1, n):
            above = dp[j]
            best = above if above > left else left
            left = best + row[j]
            dp[j] = left
    return dp[-1]