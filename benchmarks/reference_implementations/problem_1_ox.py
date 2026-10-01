def longest_common_subsequence(s1, s2):
    """Return the length of the longest common subsequence of two strings.

    This implementation uses a bit‑parallel algorithm (Myers 1986).
    It runs in O((len(s1) * len(s2)) / wordsize) time and O(min(len(s1), len(s2))) bits of extra memory.
    """
    # Ensure the first string is the shorter one – the bitset size depends on it.
    if len(s1) > len(s2):
        s1, s2 = s2, s1
    m = len(s1)
    if m == 0:
        return 0

    # Build a mask for each character: bit i is 1 iff s1[i] equals the character.
    char_mask = {}
    for i, ch in enumerate(s1):
        # Using dict.setdefault is a tiny overhead; manual get‑or‑set is faster.
        char_mask[ch] = char_mask.get(ch, 0) | (1 << i)

    # S holds the DP state as a bitset.
    S = 0
    for ch in s2:
        # Bitmask of positions in s1 that match the current character.
        M = char_mask.get(ch, 0)
        # Myers' recurrence using only bitwise operations.
        X = M | S
        Y = (S << 1) | 1
        S = X & ~ (X - Y)

    # The number of set bits in S equals the LCS length.
    return S.bit_count()
