# Python CLI — click Patterns

## Command Architecture

- Thin entry point (`cli.py`) that only assembles the group with `add_command` — no logic, no options, no imports beyond the command functions
- Co-locate click commands with the module that owns their logic: `linker.py` defines `install` and `update`, `config.py` defines `status`
- When adding a new command, put it in the module it naturally belongs to; `cli.py` only changes to register it

## Help Text as Documentation

The `--help` output is often the first thing users see. Make it count.

- Write descriptive docstrings on every command — click uses them as help text
- Use `click.Choice` for options with a known set of values — lists valid options in help output and validates input automatically
- Add `help=` to every option — describe what it does, not just what it's called
- Keep argument names self-explanatory: `TARGET` not `PATH`, `QUERY` not `INPUT`

```python
# Good — help shows available profiles and describes behavior
@click.option(
    "--profile",
    type=click.Choice(["astro", "nextjs", "python"]),
    help="Profile to install (omit for interactive selection).",
)

# Bad — no guidance, user has to guess valid values
@click.option("--profile", help="Profile name.")
```

## Parameter Types

- `click.Path(exists=True, file_okay=False, path_type=Path)` for directory arguments
- `click.Choice` for closed sets of string values — provides validation and help text
- `click.IntRange` / `click.FloatRange` for bounded numbers
- `path_type=Path` on all path parameters — never work with raw strings

## Interactive Input

- `click.prompt()` for interactive input — not raw `input()`
- `click.confirm()` for yes/no questions
- Provide a non-interactive alternative for every interactive prompt (e.g., `--profile` flag skips profile selection)
- Commands MUST work in scripts — if `--flag` can replace a prompt, document it

## Error Handling

- `raise SystemExit(1)` for user errors — not `sys.exit()` (testable without mocking)
- Print clear error messages before exiting — what went wrong and what to do about it
- Use `click.UsageError` for invalid argument combinations
- Let click handle validation for `Choice`, `Path`, and `IntRange` — don't duplicate their checks

## Output

- Use `rich` for colored, structured output — not raw `print()`
- Status/progress for operations that take time
- Summary at the end of multi-step operations (e.g., "3 linked, 1 updated, 1 skipped")
- Errors to stderr (rich `Console(stderr=True)` or click's `echo(err=True)`)

## Testing CLI Commands

- Test the core logic function, not the click command wrapper
- Click commands are thin — they parse arguments, call logic, format output
- Use `click.testing.CliRunner` only for integration tests of argument parsing
- Never mock the filesystem — use `tmp_path` fixtures with real files

## Anti-Patterns

| Pattern | Problem | Fix |
| --- | --- | --- |
| Logic in click command | Untestable without CliRunner | Extract logic into plain function |
| `input()` / `print()` | Not click-aware, no color, no testing | `click.prompt()` / `rich` console |
| Manual validation for Choice-like options | Duplicated logic, no help text | `click.Choice` |
| `sys.exit()` | Requires mocking in tests | `raise SystemExit` |
| Hard-coded option values in help strings | Drifts out of sync | Derive from config or constants |
| All commands in `cli.py` | Monolithic, unrelated logic together | Co-locate with owning module |
