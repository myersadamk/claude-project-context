# Python Tools — Review Checklist

## Verification Commands

All MUST pass before approval:

```bash
python3 -I -m compileall -q .
```

Then run every self-check script the changed tools have (the project's CLAUDE.md lists them), each with `python3 -I`, and read its `PASS`/`FAIL` line. Blender scripts are checked by running them headless and reading their `RESULT` lines.

## Checklist

### Scripts (-> python-tools-scripts.md)

- [ ] Run with `python3 -I`; sibling imports add their own directory to `sys.path`
- [ ] Standard library only
- [ ] `if __name__ == "__main__":` guard, `argparse`, non-zero exit and a summary line on failure
- [ ] `subprocess` with argument lists and timeouts, no `shell=True`

### Determinism (-> python-tools-scripts.md)

- [ ] Every random draw comes from an explicit `random.Random(seed)`
- [ ] No set iteration order or directory order reaches output
- [ ] Text files opened with `encoding="utf-8"`

### References

- [ ] Written from the spec, not from the code under test
- [ ] Float operation order matches the spec; expected values in a committed `.expected.txt`

### Blender (-> python-tools-blender.md)

- [ ] `--python-exit-code 1`, script args after `--`
- [ ] Version header and version check
- [ ] Outputs checked by structure, not bytes; postconditions fail loudly
