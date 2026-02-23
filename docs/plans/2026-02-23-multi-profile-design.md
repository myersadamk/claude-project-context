# Multi-Profile Support

> Install multiple profiles into a single target project. Uninstall individually. Update refreshes all.

## Problem

Running `cpc install --profile=flutter-app` on a repo that already has `python-cli` uninstalls python-cli. This is because the sync logic treats the new profile as the complete desired state and cleans anything outside it.

Real projects often need multiple profiles — e.g. a Flutter app with a Python CLI backend.

## CLI Surface

```
cpc install <target> --profile=flutter-app    # additive — joins existing profiles
cpc uninstall <target> --profile=python-cli   # removes one profile, keeps the rest
cpc update <target>                           # re-syncs all installed profiles
```

- `install` is always additive. Installing an already-installed profile is a no-op (or refresh).
- `uninstall` removes one profile. Shared symlinks survive if another profile still needs them.
- `update` iterates all installed profiles (unchanged conceptually).

## Manifest

```json
{
  "source": "/path/to/cpc",
  "profiles": ["python-cli", "flutter-app"],
  "installed": "2026-02-23"
}
```

- `profile` (string) → `profiles` (list of strings)
- `rules` and `skills` fields dropped — derived at runtime as the union from config.yaml
- Backward compatibility: `load_manifest` detects old `profile` key → migrates to `profiles: [profile]`

## Sync Logic

The core insight: `install_profile()` already takes generic `rule_sets` and `skill_dirs`. It doesn't need to change. The change is in **what we pass to it** — a union of all installed profiles instead of a single profile's lists.

### Install flow

1. Load manifest → `profiles: [python-cli]`
2. Append → `profiles: [python-cli, flutter-app]`
3. Compute union of rules: `{universal-coding, python-cli, flutter-app}`
4. Compute union of skills: `{cpc-init, cpc-audit, cpc-extract, flutter-interface-design, vibesec}`
5. `install_profile()` with the full union — existing symlinks survive
6. Save manifest, update .gitignore

### Uninstall flow

1. Load manifest → `profiles: [python-cli, flutter-app]`
2. Remove → `profiles: [flutter-app]`
3. Compute union of remaining: rules `{universal-coding, flutter-app}`, skills `{flutter-interface-design, vibesec, cpc-init, cpc-audit, cpc-extract}`
4. `install_profile()` with reduced union — python-cli-*.md symlinks cleaned by `_clean_stale_symlinks`
5. Save manifest, update .gitignore

### Uninstall last profile

When uninstalling the last remaining profile:
- Remove all cpc-owned symlinks (union is empty → everything is stale)
- Delete the manifest file
- Clean the cpc section from .gitignore
- Target repo returns to pre-cpc state

## Code Changes

### `config.py`

- `Manifest.profile` (str) → `Manifest.profiles` (list[str])
- Drop `Manifest.rules` and `Manifest.skills` fields
- `load_manifest`: detect old format (`"profile"` key) → return `profiles: [profile]`
- `save_manifest(target, profiles: list[str])` — accepts profile name list instead of Profile object
- New: `resolve_profiles(profile_names: list[str], config: Config) → tuple[list[RuleSet], list[Path]]` — computes the union of rules and resolved skill dirs across all named profiles

### `linker.py`

- `install` command: load manifest (or empty), append profile, compute union via `resolve_profiles`, call `install_profile` with union, save manifest
- `update` command: load manifest, compute union of all profiles, sync, save manifest
- New `uninstall` command: load manifest, remove profile from list, if empty → clean everything + delete manifest + clean .gitignore; otherwise compute remaining union, sync, save manifest
- `_gitignore_from_profile` → `_gitignore_from_profiles(target, profile_names, config)` — computes union for .gitignore entries

### `install_profile()` — No changes

Already takes generic `rule_sets` and `skill_dirs` and syncs to that set.

## Tests

- **Additive install:** install A, install B → both sets of symlinks present
- **Uninstall one:** install A+B, uninstall A → only B symlinks remain
- **Shared resources survive:** install A+B (both have cpc-audit), uninstall A → cpc-audit still linked
- **Update refreshes all:** install A+B, update → all symlinks refreshed
- **Manifest migration:** old single-profile manifest loads correctly as `profiles: [name]`
- **Uninstall last profile:** install A, uninstall A → no manifest, no symlinks, clean .gitignore
- **Uninstall non-installed profile:** error message
- **Install already-installed profile:** no-op or refresh, no duplicate in manifest
- **Gitignore reflects union:** install A+B → .gitignore has entries from both; uninstall A → only B entries remain
