# Python CLI — Typing

## Core Principle

Types encode domain knowledge. A function signature should tell you what it expects without reading the implementation.

## NewType for Validated Strings

Use `NewType` when a string has been validated or has domain meaning beyond "arbitrary text."

```python
from typing import NewType

RuleSet = NewType("RuleSet", str)
ProfileName = NewType("ProfileName", str)
```

- Construct at the validation boundary (config loading, CLI parsing) — not deep in business logic
- Downstream functions accept the `NewType`, not bare `str`
- Zero runtime cost — it's just `str` at runtime, but type checkers treat it as distinct
- Prefer over `StrEnum` when the set of values is dynamic or discovered at runtime
- Prefer `StrEnum` when the set is small, fixed, and benefits from exhaustive matching

| Scenario | Use |
| --- | --- |
| Fixed, small set (3-5 values) | `StrEnum` |
| Dynamic set (discovered from filesystem, config, API) | `NewType` |
| Arbitrary string with no domain meaning | `str` |

## Frozen Dataclasses Over Dicts

All structured data uses `@dataclass(frozen=True)`. No untyped dicts flowing between functions.

```python
@dataclass(frozen=True)
class Profile:
    name: str
    rules: list[RuleSet]
    skills: list[str]
```

- `frozen=True` on every dataclass — config and results are immutable data, not mutable state
- Use `field(default_factory=list)` for mutable defaults, never bare `[]`
- Derived properties use `@property`, not pre-computed fields
- No `TypedDict` — dataclasses are more explicit and support methods

## Path Not str

`Path` for all filesystem values — type safety, no ambiguity about what a string represents.

- Accept `Path` parameters, not `str` — let callers convert at the boundary
- `click.Path(path_type=Path)` on all CLI path arguments
- Never `str(path)` for path operations — use `Path` methods

## Union Syntax

- `str | None` (3.10+), not `Optional[str]`
- `from __future__ import annotations` when using forward references or union syntax in older runtimes

## No Any

If the type is genuinely unknown, validate and narrow — don't use `Any` as an escape hatch.

## Explicit Return Types

Every function declares its return type. This catches bugs where a function accidentally returns `None` from a missing branch.

## Anti-Patterns

| Pattern | Problem | Fix |
| --- | --- | --- |
| Bare `str` for domain values | No distinction between validated and unvalidated | `NewType` or `StrEnum` |
| `dict` between functions | No type safety, no IDE support | `@dataclass(frozen=True)` |
| `str` for file paths | Ambiguous, no path operations | `Path` |
| `Optional[X]` | Verbose, old syntax | `X \| None` |
| `Any` | Disables type checking entirely | Specific types or validate + narrow |
| `isinstance` chains | Fragile, not exhaustive | `match` statement or `StrEnum` |
| Mutable default arguments | Shared state between calls | `field(default_factory=...)` or `None` |
