from __future__ import annotations
import sys
import time
from typing import Generator, Iterable

def _digit_pairs(n: int, digits: int) -> list[int]:
    """
    Split integer n into 2-digit pairs (left to right), then append `digits`
    zero-pairs for fractional precision.
    """
    s = str(n)
    if len(s) % 2 == 1:
        s = "0" + s
    pairs = [int(s[i:i + 2]) for i in range(0, len(s), 2)]
    if digits > 0:
        pairs.extend([0] * digits)
    return pairs

def trace_aryabhata(n: int, digits: int = 0) -> Generator[dict, None, None]:
    """
    Yield a detailed trace of Aryabhata's digit-pair square-root extraction.

    Each yielded dict includes per-trial info while choosing the next digit x:

        {
          "pair_index": int,       # 0-based
          "pair_value": int,       # the next 2-digit block
          "root_before": int,
          "remainder_before": int,
          "divisor": int,          # D = 20 * root_before
          "trial": int,            # 0..9 (emitted for each trial)
          "fits": bool,            # (D + trial) * trial <= remainder_before'
          "chosen": bool,          # True only on the chosen x
          "root_after": int,       # only on the chosen x
          "remainder_after": int   # only on the chosen x
        }

    Consumers can animate by listening to every trial and highlighting the chosen one.
    """
    pairs = _digit_pairs(n, digits)

    first = pairs[0]
    root = int(first ** 0.5)
    remainder = first - root * root
    yield {
        "pair_index": 0,
        "pair_value": first,
        "root_before": 0,
        "remainder_before": first,
        "divisor": 0,
        "trial": root,
        "fits": True,
        "chosen": True,
        "root_after": root,
        "remainder_after": remainder
    }

    for idx, p in enumerate(pairs[1:], start=1):
        remainder = remainder * 100 + p
        D = 20 * root

        last_fit = 0
        for t in range(0, 10):
            fits = (D + t) * t <= remainder
            if fits:
                last_fit = t
            yield {
                "pair_index": idx,
                "pair_value": p,
                "root_before": root,
                "remainder_before": remainder,
                "divisor": D,
                "trial": t,
                "fits": fits,
                "chosen": False,
                "root_after": None,
                "remainder_after": None
            }
            if not fits and t > 0:
                break

        x = last_fit
        remainder_after = remainder - (D + x) * x
        root_after = root * 10 + x
        root, remainder = root_after, remainder_after

        yield {
            "pair_index": idx,
            "pair_value": p,
            "root_before": root // 10,
            "remainder_before": remainder + (D + x) * x,
            "divisor": D,
            "trial": x,
            "fits": True,
            "chosen": True,
            "root_after": root_after,
            "remainder_after": remainder_after
        }

def animate_trace(n: int, digits: int = 0, fps: int = 12, stream=sys.stdout) -> None:
    """
    Render the trace as an ASCII animation. If the output is not a TTY, we fall back
    to a simple step log so you can still pipe it to a file without garbage ANSI codes.
    """
    is_tty = hasattr(stream, "isatty") and stream.isatty()
    frame_delay = 1.0 / max(1, fps)

    def clear():
        if is_tty:
            stream.write("\x1b[2J\x1b[H")
        else:
            stream.write("\n")

    def write_frame(d: dict):
        chosen = d["chosen"]
        t = d["trial"]
        idx = d["pair_index"]
        pairv = d["pair_value"]
        root_b = d["root_before"]
        rem_b = d["remainder_before"]
        D = d["divisor"]

        header = f" Aryabhata √ (n={n}, digits={digits}) ".center(64, "=")
        footer = "=" * 64
        line1 = f"pair[{idx}] = {pairv:02d}   D = 20·R = {D}"
        line2 = f"R(before) = {root_b}    rem(before) = {rem_b}"
        trial_line = f"try x = {t}  →  (D + x)·x = {(D + t) * t}"

        if chosen:
            root_a = d["root_after"]
            rem_a = d["remainder_after"]
            verdict = "✓ chosen"
            line3 = f"R(after)  = {root_a}    rem(after)  = {rem_a}"
        else:
            verdict = "fits" if d["fits"] else "nope"
            line3 = ""

        if is_tty:
            strong = "\x1b[1m" if chosen else ""
            reset = "\x1b[0m" if chosen else ""
            trial_line = f"{strong}{trial_line:<30} {verdict}{reset}"
        else:
            trial_line = f"{trial_line:<30} {verdict}"

        clear()
        stream.write(f"{header}\n{line1}\n{line2}\n{trial_line}\n{line3}\n{footer}\n")
        stream.flush()

    last_idx = -1
    for step in trace_aryabhata(n, digits):
        write_frame(step)
        time.sleep(frame_delay * (2.0 if step["chosen"] or step["pair_index"] != last_idx else 1.0))
        last_idx = step["pair_index"]

def dump_trace(n: int, digits: int = 0, stream=sys.stdout) -> None:
    """
    Non-animated fallback: print a readable step log (one line per chosen digit).
    """
    stream.write(f"Trace for n={n}, digits={digits}\n")
    for d in trace_aryabhata(n, digits):
        if d["chosen"]:
            stream.write(
                f"[pair {d['pair_index']}] pair={d['pair_value']:02d} "
                f"D={d['divisor']} x={d['trial']}  "
                f"R:{d['root_before']}→{d['root_after']}  "
                f"rem:{d['remainder_before']}→{d['remainder_after']}\n"
            )
    stream.flush()
