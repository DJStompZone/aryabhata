from __future__ import annotations
import argparse
import sys

from aryabhata.sqrt import sqrt_aryabhata
from aryabhata.trace import animate_trace, dump_trace

def _print_err(e: Exception, source: str = ""):
    source = f"[{source}] " if source else ""
    print(f"{source}Unexpected {e.__class__.__name__} encountered")

def _check_tty() -> bool:
    try:
        return hasattr(sys.stdout, "isatty") and sys.stdout.isatty
    except Exception as e:
        _print_err(e, "_check_tty")
        return False

def _format_decimal_from_scaled(scaled_root: int, digits: int) -> str:
    """
    Convert the scaled integer root (root * 10**digits) into a zpad decimal string.
    Example: 9055, 3 -> "9.055"; digits=0 -> "9055".
    """
    if digits <= 0:
        return str(scaled_root)
    ip = scaled_root // (10 ** digits)
    fp = scaled_root % (10 ** digits)
    return f"{ip}.{fp:0{digits}d}"


def main(argv=None) -> None:
    """
    CLI frontend for Aryabhata's digit-pair square root.

    Default:
      Prints only the decimal result.

    Flags:
      --debug     Also show scaled root, remainder, and identity.
      --animate   Play an ASCII animation of the digit-pair extraction.
      --fps N     Animation frames per second (default 12).
      --trace     If not a TTY, print a readable step log instead of frames.
    """

    p = argparse.ArgumentParser(
        prog="aryabhata",
        description="Aryabhata digit-pair square root calculator"
    )
    p.add_argument("n", type=int, help="integer radicand")
    p.add_argument("--digits", type=int, default=0, help="fractional digits to compute")
    p.add_argument("--debug", action="store_true", help="show raw scaled root + remainder")
    p.add_argument("--animate", action="store_true", help="ASCII animation of extraction")
    p.add_argument("--fps", type=int, default=12, help="frames per second for animation")
    p.add_argument("--trace", action="store_true",
                   help="when not a TTY, print a static step trace instead of raw result")
    args = p.parse_args(argv)

    root, rem = sqrt_aryabhata(args.n, digits=args.digits)

    print(_format_decimal_from_scaled(root, args.digits))

    if args.debug:
        print(f"[scaled-root] {root}")
        print(f"[remainder]   {rem}")
        N = args.n * (10 ** (2 * args.digits))
        print(f"[identity]    {N} = {root}^2 + {rem}")

    if args.animate:
        try:
            if _check_tty():
                return animate_trace(args.n, args.digits, fps=max(1, args.fps), stream=sys.stdout)
            if args.trace:
                return dump_trace(args.n, args.digits, stream=sys.stdout)
            print("The animate flag was set, but failed to detect required conditions for animation.")
        except Exception as e:
            _print_err(e, "main//animate")
            raise e
