# Python CLI — Review

## Verification Commands

All MUST pass before approval:

```bash
uv run pytest
```

## Checklist

### CLI Patterns (-> python-cli-click.md)

- [ ] Click commands are thin — logic extracted into plain functions
- [ ] `click.Choice` for closed option sets, not manual validation
- [ ] `click.Path(path_type=Path)` on all path parameters
- [ ] `raise SystemExit(1)` for errors, not `sys.exit()`
- [ ] `rich` for output, not raw `print()`

### Typing (-> python-cli-typing.md)

- [ ] `NewType` for validated domain strings
- [ ] `@dataclass(frozen=True)` for structured data, no untyped dicts
- [ ] `Path` not `str` for filesystem values
- [ ] Explicit return types on all functions
- [ ] No `Any`

### Best Practices (-> python-cli-best-practices.md)

- [ ] Keyword-only args for functions with 3+ similar-typed parameters
- [ ] `relative_to()` for path ancestry checks, never string matching
- [ ] `is_symlink()` before `exists()` when handling symlinks
- [ ] Tests use real filesystem (`tmp_path`), no mocking
