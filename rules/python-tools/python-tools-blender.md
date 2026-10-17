---
paths:
  - "**/blender/**/*.py"
---

# Python Tools — Blender as Code

Scripts that Blender runs headless to make assets. The script, its arguments and its seed are the source; the files it writes are build products.

## Running Headless

- MUST run `blender -b --python-exit-code 1 -P <script> -- <args>`. Without `--python-exit-code`, an exception in the script still exits 0 and the caller thinks it worked.
- Script arguments MUST come after `--` and be read from `sys.argv[sys.argv.index("--") + 1:]`. Blender ignores everything after `--`.
- Blender runs its arguments in the order given. Put `-b` first and `-P` after any file to load.
- Blender's Python ignores `PYTHONPATH` unless started with `--python-use-system-env`. Scripts MUST add their own directory to `sys.path` to import siblings.
- Add-ons and extensions a script needs MUST be enabled inside the script (`addon_utils.enable(..., default_set=True)`). In background mode, an installed extension isn't necessarily registered.
- SHOULD start from a known empty scene: `bpy.ops.wm.read_factory_settings(use_empty=True)`.

## Versions

- MUST record the Blender version (and each add-on's version) in the script's header, and SHOULD check `bpy.app.version` at startup and fail on a mismatch. The `bpy` API changes between major versions: in Blender 5, actions are slotted and `action.fcurves` is gone.
- SHOULD type-check against stubs for the pinned version (`fake-bpy-module-<version>` with pyright).

## Determinism

- MUST seed every random choice from an explicit `random.Random(seed)`. Add-ons may use the global `random`; never depend on its state.
- MUST check outputs by structure (vertex and bone counts, names, bounds, written to a sidecar JSON), not by file bytes. Some operators aren't deterministic run to run (UV island packing is one), so byte equality is the wrong contract.
- MUST select objects, bones and materials by name, never by list index.
- MUST verify postconditions and fail loudly (exit 1 with a `RESULT … FAIL` line): a modifier that silently didn't apply, a missing armature, unweighted vertices.

## Output

- MUST print greppable result lines (`RESULT <check>: PASS|FAIL …`). Blender's own log is noisy.
- MUST write scratch output to a gitignored folder inside the project, never next to committed assets.
- A Windows Blender driven from WSL can only see Windows paths: convert with `wslpath -w`, and keep outputs on the Windows drive.

## Anti-Patterns

| Pattern | Problem | Fix |
| --- | --- | --- |
| `blender -b -P x.py` | A Python error exits 0 | Add `--python-exit-code 1` |
| `bpy.data.objects[0]` | Order isn't a contract | Look up by name |
| Comparing GLB bytes | Fails on harmless churn | Compare a structural sidecar |
| Untagged script | Breaks silently on the next Blender | Version header and `bpy.app.version` check |
