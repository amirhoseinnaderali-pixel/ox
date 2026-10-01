def matrix_max_path_sum(matrix):
    """
    Modifies input matrix to save space (use only if modification is allowed).
    Most space-efficient but destructive.
    """
    if not matrix or not matrix[0]:
        return 0
    
    m, n = len(matrix), len(matrix[0])
    
    # Fill first row
    for j in range(1, n):
        matrix[0][j] += matrix[0][j - 1]
    
    # Fill first column
    for i in range(1, m):
        matrix[i][0] += matrix[i - 1][0]
    
    # Fill rest of matrix
    for i in range(1, m):
        for j in range(1, n):
            matrix[i][j] += max(matrix[i - 1][j], matrix[i][j - 1])
    
    return matrix[m - 1][n - 1]

