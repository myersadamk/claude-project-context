# Python CLI — Review Checklist

## Verification Commands

All MUST pass before approval:

```bash
uv run pytest
```

## Checklist

### Python Quality (-> python-cli-best-practices.md)

- [ ] Keyword-only arguments for functions with 3+ similar-typed parameters
- [ ] `Path` parameters, not `str`
- [ ] `raise SystemExit(1)`, not `sys.exit()`
- [ ] Specific exceptions, no bare `except:` or `except Exception:`

### CLI (-> python-cli-click.md)

- [ ] Click commands are thin — logic extracted into plain functions
- [ ] `click.Choice` for closed sets, `click.Path(path_type=Path)` for paths
- [ ] `help=` on every option
- [ ] Non-interactive alternative for every interactive prompt

### Types (-> python-cli-typing.md)

- [ ] No `Any` or `cast()` without justification
- [ ] Dataclasses or `TypedDict` for structured data, not raw dicts
- [ ] `NewType` for domain identifiers

### Filesystem Safety

- [ ] `relative_to()` with `try/except ValueError` for path ancestry — no string matching
- [ ] `is_symlink()` before `exists()` when handling symlinks
- [ ] Never `unlink()` without verifying `is_symlink()` first
