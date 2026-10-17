---
paths:
  - "**/*.py"
---

# Python Tools — Standalone Scripts

For tool scripts that live inside another project (generators, reference implementations, checkers, drivers): no package, no dependencies, run directly. A packaged CLI with dependencies follows `python-cli` instead.

## Running

- MUST run scripts as `python3 -I <script>`. Isolated mode drops the script's directory and user site-packages from `sys.path` and ignores every `PYTHON*` variable, so a stray `json.py` next to the data can't shadow the standard library.
- A script that imports a sibling MUST add its own directory explicitly: `sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))`. `-I` no longer does it for you.
- MUST use only the standard library. Needing a dependency means it has become a `python-cli` project.
- MUST guard the entry point with `if __name__ == "__main__":`, so tests and other scripts can import the functions.
- MUST use `argparse`, exit non-zero on failure, and print one greppable summary line: `NAME: PASS (…)` / `NAME: FAIL (…)`.
- MUST call other programs with `subprocess.run([...], check=True, timeout=…)` and an argument list. MUST NOT use `shell=True`.

## Determinism

- MUST draw randomness from an explicit `random.Random(seed)` passed in. MUST NOT call module-level `random.*`: it's one global stream that libraries draw from too.
- MUST NOT let the iteration order of a `set` or `frozenset` of strings reach output. String hashes are randomized per process, and `-I` ignores `PYTHONHASHSEED`, so the order can't be pinned. Sort first. (`dict` keeps insertion order; that's guaranteed.)
- MUST sort directory listings (`sorted(Path.iterdir())`, `sorted(glob(...))`). The OS order is arbitrary.
- MUST open text files with `encoding="utf-8"` and, when writing, `newline="\n"`. The defaults depend on the platform and locale.

## Restating another language's spec

When a script is an independent reference (it produces expected values for another language's tests):

- MUST be written from the spec text, never by reading or porting the code under test. A reference copied from the code agrees with its bugs.
- MUST perform floating-point operations in the order the spec gives. `sum()` of floats uses compensated summation since Python 3.12, so `sum([a, b, c])` can differ from `a + b + c` in the last bit. Use whichever the spec means, and say so in a comment.
- MUST mind the semantics that differ from C-family languages: `%` and `//` floor toward negative infinity (C# truncates toward zero), `round()` rounds half to even, and `int(x)` truncates.
- MUST print expected values to a committed `.expected.txt` and compare byte for byte, rather than retyping values into tests.

## Windows Programs from WSL

- Paths handed to a Windows program MUST be converted with `wslpath -w`. It fails on a path that doesn't exist yet: convert the parent and append the name.
- MUST strip `\r` from a Windows program's output before parsing it.

## Anti-Patterns

| Pattern | Problem | Fix |
| --- | --- | --- |
| `random.random()` | Global stream, shared with libraries | `rng = random.Random(seed)` passed in |
| `for name in set_of_names:` into output | Order changes every run | `for name in sorted(...)` |
| `python3 script.py` | Script dir and env can inject modules | `python3 -I script.py` |
| Reference ported from the code under test | Agrees with the code's bugs | Write it from the spec |
| `open(path)` for text | Locale-dependent encoding | `open(path, encoding="utf-8")` |
