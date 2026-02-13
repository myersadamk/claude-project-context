# Python Best Practices

## Types and Data Structures

- `frozen=True` on all dataclasses — config and results are immutable data, not mutable state
- `StrEnum` for closed sets of string values — IDE autocomplete, exhaustive matching, serializes as plain string
- `Path` not `str` for all filesystem paths — type safety, no ambiguity about what a string represents
- `str | None` union syntax (3.10+), not `Optional[str]`
- No `Any` — if the type is genuinely unknown, use `unknown` patterns (validate and narrow)
- No untyped dicts flowing between functions — define a dataclass or `TypedDict`
- Explicit return types on all functions

## Function Signatures

- Keyword-only arguments (`*`) for functions with 3+ parameters of similar types
- Default values for optional parameters, not `None` sentinel checks
- Accept `Path` parameters, not `str` — let callers convert at the boundary

## Naming

- `snake_case` for functions, variables, modules
- `PascalCase` for classes, dataclasses, enums
- `UPPER_SNAKE_CASE` for module-level constants
- Private helpers prefixed with `_` (single underscore)
- Boolean variables: prefix with `is_`, `has_`, `should_`
- No abbreviations in public APIs — `configuration` not `cfg`, `manifest` not `mfst`

## Imports

- Standard library first, blank line, third-party, blank line, local imports
- `from __future__ import annotations` when using forward references or `str | None` syntax in older runtimes
- No wildcard imports (`from x import *`)
- Prefer explicit imports over module-level imports for clarity

## Filesystem Safety

- `relative_to()` with `try/except ValueError` for path ancestry checks — never use string matching (`str(path) in str(other)`)
- `is_symlink()` before `exists()` when handling symlinks — a broken symlink returns `True` for `is_symlink()` but `False` for `exists()`
- Never `unlink()` without first verifying `is_symlink()` — protect real files from accidental deletion
- Use `os.path.relpath()` for relative symlinks — keeps symlinks portable within a directory structure

## Error Handling

- Validate at system boundaries (CLI input, config files, external data) — not between internal functions
- Use specific exceptions, not bare `except:` or `except Exception:`
- `raise SystemExit(1)` in CLI commands, not `sys.exit()` — testable without mocking
- Let TypeErrors and AttributeErrors propagate — they indicate bugs, not user errors

## Project Structure

- `src/` layout for packages (`src/package/`)
- `pyproject.toml` for all project metadata — no `setup.py`, `setup.cfg`, or `requirements.txt`
- `uv` for dependency management and script execution
- Tests in `tests/` at project root, mirroring source structure

## Testing

- `pytest` as the runner
- Real filesystem operations with `tmp_path` fixtures — no mocking the filesystem
- Safety invariants tested first — if destructive operations can happen, prove they don't
- TDD for safety-critical code: write failing tests before implementation
- Test behavior, not implementation details

## Anti-Patterns

| Pattern | Why | Use Instead |
| --- | --- | --- |
| `Any` | Disables type checking | Specific types or `unknown` + narrowing |
| `dict` as a data structure between functions | No type safety, no IDE support | `dataclass` or `TypedDict` |
| `str` for file paths | Ambiguous, no path operations | `Path` |
| `Optional[X]` | Verbose, old syntax | `X \| None` |
| `isinstance` chains | Fragile, not exhaustive | `match` statement or `StrEnum` |
| String matching for path checks | Breaks on similar prefixes | `Path.relative_to()` |
| `sys.exit()` in library code | Untestable | `raise SystemExit` or return error types |
| Mutable default arguments | Shared state between calls | `field(default_factory=list)` or `None` sentinel |
