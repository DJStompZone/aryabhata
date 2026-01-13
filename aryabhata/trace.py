from __future__ import annotations

import os
import sys
import time
from typing import Generator


def _digit_pairs(n: int, digits: int) -> list[int]:
    """Split integer n into 2-digit pairs (left->right), then append `digits` zero-pairs."""
    s = str(n)
    if len(s) % 2 == 1:
        s = "0" + s
    pairs = [int(s[i:i + 2]) for i in range(0, len(s), 2)]
    if digits > 0:
        pairs.extend([0] * digits)
    return pairs


def _format_decimal_from_scaled(scaled_root: int, digits: int) -> str:
    """Render scaled_root as a zero-padded decimal string, e.g. 9055,3 -> '9.055'."""
    if digits <= 0:
        return str(scaled_root)
    scale = 10 ** digits
    ip = scaled_root // scale
    fp = scaled_root % scale
    return f"{ip}.{fp:0{digits}d}"


def _supports_color(stream) -> bool:
    """True if ANSI color likely works on this stream without extra deps."""
    if not (hasattr(stream, "isatty") and stream.isatty()):
        return False
    if os.environ.get("NO_COLOR"):
        return False
    term = os.environ.get("TERM", "")
    if term.lower() == "dumb":
        return False
    return True


def _ansi(enabled: bool):
    """Small ANSI palette."""
    if not enabled:
        return {
            "reset": "",
            "bold": "",
            "dim": "",
            "inv": "",
            "cyan": "",
            "green": "",
            "red": "",
            "yellow": "",
            "gray": "",
        }
    return {
        "reset": "\x1b[0m",
        "bold": "\x1b[1m",
        "dim": "\x1b[2m",
        "inv": "\x1b[7m",
        "cyan": "\x1b[36m",
        "green": "\x1b[32m",
        "red": "\x1b[31m",
        "yellow": "\x1b[33m",
        "gray": "\x1b[90m",
    }


def _highlight_last_digit(s: str, prefix: str, suffix: str) -> str:
    """Wrap the last numeric digit in s with prefix/suffix."""
    for i in range(len(s) - 1, -1, -1):
        if s[i].isdigit():
            return s[:i] + prefix + s[i] + suffix + s[i + 1:]
    return s


def trace_aryabhata(n: int, digits: int = 0) -> Generator[dict, None, None]:
    pairs = _digit_pairs(n, digits)

    first_pair = pairs[0]
    root = int(first_pair ** 0.5)
    remainder = first_pair - root * root

    yield {
        "pair_index": 0,
        "pair_value": first_pair,
        "pairs_total": len(pairs),
        "digits": digits,
        "root_before": 0,
        "root_after": root,
        "divisor": 0,
        "trial": root,
        "fits": True,
        "chosen": True,
        "carry_before": first_pair,
        "expanded": first_pair,
        "carry_after": remainder,
        "subtracted": root * root,
    }

    for idx, pair in enumerate(pairs[1:], start=1):
        carry_before = remainder
        expanded = carry_before * 100 + pair
        D = 20 * root

        last_fit = 0

        yield {
            "pair_index": idx,
            "pair_value": pair,
            "pairs_total": len(pairs),
            "digits": digits,
            "root_before": root,
            "root_after": None,
            "divisor": D,
            "trial": 0,
            "fits": True,
            "chosen": False,
            "carry_before": carry_before,
            "expanded": expanded,
            "carry_after": None,
            "subtracted": 0,
        }

        for t in range(1, 10):
            prod = (D + t) * t
            fits = prod <= expanded
            if fits:
                last_fit = t

            yield {
                "pair_index": idx,
                "pair_value": pair,
                "pairs_total": len(pairs),
                "digits": digits,
                "root_before": root,
                "root_after": None,
                "divisor": D,
                "trial": t,
                "fits": fits,
                "chosen": False,
                "carry_before": carry_before,
                "expanded": expanded,
                "carry_after": None,
                "subtracted": prod,
            }

            if not fits:
                break

        x = last_fit
        sub = (D + x) * x
        carry_after = expanded - sub
        root_after = root * 10 + x

        root = root_after
        remainder = carry_after

        yield {
            "pair_index": idx,
            "pair_value": pair,
            "pairs_total": len(pairs),
            "digits": digits,
            "root_before": root_after // 10,
            "root_after": root_after,
            "divisor": D,
            "trial": x,
            "fits": True,
            "chosen": True,
            "carry_before": carry_before,
            "expanded": expanded,
            "carry_after": carry_after,
            "subtracted": sub,
        }


def dump_trace(n: int, digits: int = 0, stream=sys.stdout) -> None:
    stream.write(f"Trace for n={n}, digits={digits}\n")
    for d in trace_aryabhata(n, digits):
        if d["chosen"]:
            root_before = _format_decimal_from_scaled(d["root_before"], digits)
            root_after = _format_decimal_from_scaled(d["root_after"], digits)
            stream.write(
                f"[pair {d['pair_index']}] pair={d['pair_value']:02d} "
                f"D={d['divisor']} x={d['trial']} "
                f"R:{root_before}→{root_after} "
                f"carry:{d['carry_before']} expanded:{d['expanded']} "
                f"sub:{d['subtracted']} carry_next:{d['carry_after']}\n"
            )
    stream.flush()


def animate_trace(n: int, digits: int = 0, fps: int = 12, stream=sys.stdout) -> None:
    is_tty = hasattr(stream, "isatty") and stream.isatty()
    if not is_tty:
        dump_trace(n, digits, stream=stream)
        return

    color_on = _supports_color(stream)
    A = _ansi(color_on)
    frame_delay = 1.0 / max(1, fps)

    pairs = _digit_pairs(n, digits)

    s_int = str(n)
    int_pairs_count = (len(s_int) + 1) // 2

    def clear():
        stream.write("\x1b[2J\x1b[H")

    def fmt_root_converging(root_int: int, pair_index: int, chosen: bool) -> str:
        committed_pairs = (pair_index + 1) if chosen else pair_index
        frac_done = max(0, committed_pairs - int_pairs_count)
        shown = min(digits, frac_done)

        if digits <= 0:
            return str(root_int)

        if shown == 0:
            return f"{root_int}.{'0' * digits}"

        scale = 10 ** shown
        ip = root_int // scale
        fp = root_int % scale
        fp_str = f"{fp:0{shown}d}" + ("0" * (digits - shown))
        return f"{ip}.{fp_str}"

    def radicand_line(active_idx: int) -> str:
        chunks = []
        for i, p in enumerate(pairs):
            token = f"{p:02d}"
            if i == active_idx:
                token = f"{A['inv']}{A['bold']}{token}{A['reset']}"
            chunks.append(token)

        if digits > 0:
            left = " ".join(chunks[:int_pairs_count])
            right = " ".join(chunks[int_pairs_count:])
            return f"radicand: {left} {A['gray']}·{A['reset']} {right}".rstrip()
        return "radicand: " + " ".join(chunks)

    def write_frame(d: dict):
        idx = d["pair_index"]
        total = d["pairs_total"]
        pairv = d["pair_value"]
        D = d["divisor"]
        t = d["trial"]
        chosen = d["chosen"]
        fits = d["fits"]

        carry_before = d["carry_before"]
        expanded = d["expanded"]
        sub = (D + t) * t
        carry_after = d["carry_after"]

        root_before = fmt_root_converging(d["root_before"], idx, chosen=False)
        root_after = fmt_root_converging(d["root_after"], idx, chosen=True) if chosen else None

        verdict = "chosen" if chosen else ("fits" if fits else "nope")

        if chosen:
            vfx = f"{A['green']}{A['bold']}{verdict}{A['reset']}"
        else:
            vfx = f"{A['green']}{verdict}{A['reset']}" if fits else f"{A['red']}{verdict}{A['reset']}"

        if chosen and root_after is not None:
            root_after = _highlight_last_digit(root_after, f"{A['yellow']}{A['bold']}", A["reset"])

        header = f"{A['cyan']}{A['bold']}Aryabhata √{A['reset']}  n={n}  digits={digits}".ljust(72)
        sep = (A["gray"] + ("=" * 72) + A["reset"]) if color_on else ("=" * 72)

        trial_line = f"try x={t} -> (D+x)*x={(D + t) * t}   {vfx}"

        current_root_scaled = d["root_after"] if chosen and d["root_after"] is not None else d["root_before"]
        approx = fmt_root_converging(current_root_scaled, idx, chosen=chosen)
        ticker = (
            f"{A['dim']}pair {idx}/{total - 1}{A['reset']}  "
            f"{A['bold']}≈{A['reset']} {approx}  "
            f"{A['dim']}carry={carry_before}{A['reset']}  "
            f"{A['dim']}expanded={expanded}{A['reset']}  "
            f"{A['dim']}D={D}{A['reset']}"
        )

        clear()
        stream.write(header + "\n")
        stream.write(sep + "\n")
        stream.write(radicand_line(idx) + "\n")
        stream.write(sep + "\n")
        stream.write(f"pair[{idx}] = {pairv:02d}    D = 20·R = {D}\n")
        stream.write(f"R(before)  = {root_before}\n")
        stream.write(f"carry      = {carry_before}\n")
        stream.write(f"expanded   = carry*100 + pair = {expanded}\n")
        stream.write(trial_line + "\n")
        stream.write(f"subtract   = {sub}\n" if chosen else "\n")
        stream.write(f"R(after)   = {root_after}\n" if chosen else "\n")
        stream.write(f"carry(next)= {carry_after}\n" if chosen else "\n")
        stream.write(sep + "\n")
        stream.write(ticker + "\n")
        stream.flush()

    last_pair_idx = -1
    for step in trace_aryabhata(n, digits):
        write_frame(step)
        multiplier = 2.0 if step["chosen"] or step["pair_index"] != last_pair_idx else 1.0
        time.sleep(frame_delay * multiplier)
        last_pair_idx = step["pair_index"]
