
from .sqrt import sqrt_aryabhata


def _format_decimal_from_scaled(scaled_root: int, digits: int) -> str:
    """
    Convert the scaled integer root (root * 10**digits)
    into a zero-padded decimal string, e.g.:

        scaled_root=9055, digits=3 --> "9.055"

    If digits=0, just return the integer as a string.
    """
    if digits <= 0:
        return str(scaled_root)

    ip = scaled_root // (10**digits)
    fp = scaled_root % (10**digits)
    return f"{ip}.{fp:0{digits}d}"


def main(argv=None):
    """
    CLI frontend for Aryabhata's digit-pair square root.

    Default behavior:
        Prints only the decimal result.

    Debug mode (--debug):
        Also prints:
          - scaled integer root
          - integer remainder
          - exact invariant details
    """
    import argparse

    p = argparse.ArgumentParser(
        prog="aryabhata",
        description="Aryabhata digit-pair square root calculator"
    )
    p.add_argument("n", type=int, help="integer radicand")
    p.add_argument("--digits", type=int, default=0,
                   help="number of fractional digits to compute")
    p.add_argument("--debug", action="store_true",
                   help="show raw scaled root + remainder")
    args = p.parse_args(argv)

    root, rem = sqrt_aryabhata(args.n, digits=args.digits)

    # pretty decimal
    print(_format_decimal_from_scaled(root, args.digits))

    if args.debug:
        print(f"[scaled-root] {root}")
        print(f"[remainder]   {rem}")
        # exact invariant
        N = args.n * (10**(2 * args.digits))
        print(f"[identity]    {N} = {root}^2 + {rem}")