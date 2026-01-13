# Aryabhata

A Python implementation of **Aryabhata’s digit‑pair square‑root algorithm** — a classical Indian arithmetic method for extracting square roots using only integer operations.

This project provides:

- A mathematically exact square‑root engine
- A modern CLI
- Optional ASCII animation of the digit‑pair extraction
- 100% unit‑test and branch coverage

---

## Features

- Exact integer arithmetic — no floating point drift
- Arbitrary precision via digit‑pair extension
- Decimal output with proper zero‑padding
- Debug mode exposing the invariant:
  `N = root² + remainder`
- Optional ASCII animation showing every digit trial
- Pytest test suite with full coverage

---

## Installation

Clone and install with Poetry:

```
git clone https://github.com/yourname/aryabhata
cd aryabhata
poetry install
```

Or install locally:

```
pip install .
```

---

## Usage

### Basic

```
python -m aryabhata 82
```

Output:

```
9
```

### With decimal precision

```
python -m aryabhata 82 --digits 3
```

Output:

```
9.055
```

### Debug mode

```
python -m aryabhata 82 --digits 3 --debug
```

Output:

```
9.055
[scaled-root] 9055
[remainder]   6975
[identity]    8200000 = 9055^2 + 6975
```

### ASCII animation

```
python -m aryabhata 82 --digits 3 --animate
```

This plays a frame‑by‑frame digit‑pair square‑root extraction in your terminal.

Control speed with:

```
--fps 15
```

---

## How the algorithm works

Aryabhata’s method operates by grouping digits into base‑100 pairs and extracting square‑root digits one at a time using this rule:

At each step:

```
Choose max x such that (20R + x)·x ≤ remainder
R := 10R + x
remainder := remainder − (20R + x)·x
```

Where `R` is the root built so far.

This is mathematically equivalent to long‑hand square‑root extraction but works entirely in integers.

---

## Library API

```python
from aryabhata.sqrt import sqrt_aryabhata

root, remainder = sqrt_aryabhata(82, digits=3)
```

Returns:

```
root = floor( sqrt(n) × 10^digits )
remainder = n × 10^(2·digits) − root²
```

---

## Testing

Run all tests with coverage:

```
poetry run coverage run -m pytest
poetry run coverage report -m
```

All code paths are fully covered.

---

## Why this exists

Most square‑root implementations hide the math behind floating point hardware.

This project exposes the **actual arithmetic** behind root extraction — the same logic used by scribes, calculators, and engineers long before digital computers existed.

It’s math you can watch happening.

---

## License

[MIT](LICENSE)
