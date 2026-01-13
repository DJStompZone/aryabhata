def sqrt_aryabhata(n, digits=0):
    """
    Aryabhata digit-pair square-root extraction.

    Args:
        n (int|float|str): Number to root. Only the integer part is used for digit pairing,
            matching the historical algorithm's integer arithmetic. Pass an integer when in doubt.
        digits (int): Number of fractional digits of precision to compute. Returns the
            floor of sqrt(n) scaled by 10**digits, plus the integer remainder.

    Returns:
        tuple[int, int]: (root, remainder) where:
            - root is floor( sqrt(n) * 10**digits )
            - remainder = n*(10**(2*digits)) - root**2

    Notes:
        The per-step test for the next digit x is:
            choose max x in 0..9 such that (20*R + x) * x <= remainder
        then update:
            remainder -= (20*R + x) * x
            R = 10*R + x
        where R is the root-so-far.
    """
    # normalize to integer string (integer part only)
    n_str = str(n).split('.')[0]

    # ensure even number of digits for pairing
    if len(n_str) % 2 == 1:
        n_str = "0" + n_str

    # pair the digits of the integer part
    pairs = [int(n_str[i:i + 2]) for i in range(0, len(n_str), 2)]

    # extend with zeros to get requested fractional digits
    if digits > 0:
        pairs.extend([0] * digits)

    # handle the degenerate case n == 0 (and digits could be 0 as well)
    if not pairs:
        return 0, 0  # pragma: no cover

    # first step: take floor(sqrt(first_pair))
    first_pair = pairs[0]
    root = int(first_pair ** 0.5)
    remainder = first_pair - root * root

    # iterate remaining pairs
    for p in pairs[1:]:
        remainder = remainder * 100 + p
        D = 20 * root

        # find the largest x with (D + x) * x <= remainder
        x = 0
        for trial in range(1, 10):
            if (D + trial) * trial <= remainder:
                x = trial
            else:
                break

        remainder -= (D + x) * x
        root = root * 10 + x

    return root, remainder
