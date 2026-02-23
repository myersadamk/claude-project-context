# Multi-Profile Support Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Allow multiple profiles to be installed simultaneously, with additive install, per-profile uninstall, and update-all semantics.

**Architecture:** Change the manifest from single-profile to multi-profile (list of strings). Compute the union of all installed profiles' rules/skills before passing to the existing `install_profile()` function, which already accepts generic rule_sets/skill_dirs. Add `uninstall` command. Update `status` to show all profiles.

**Tech Stack:** Python, Click, pytest

---

### Task 0: Create feature branch

```bash
git checkout main && git pull
git checkout -b feat/multi-profile
```

---

### Task 1: Update Manifest dataclass and load/save

The Manifest changes from single-profile to multi-profile. This is the foundation everything else builds on.

**Files:**
- Modify: `src/cpc/config.py:69-78` (Manifest dataclass)
- Modify: `src/cpc/config.py:114-132` (load_manifest)
- Modify: `src/cpc/config.py:135-152` (save_manifest)
- Test: `tests/test_linker.py`

**Step 1: Write tests for new manifest format**

Add to `tests/test_linker.py` in a new class `TestMultiProfileManifest`:

```python
class TestMultiProfileManifest:
    """Tests for multi-profile manifest format."""

    def test_save_and_load_multi_profile_manifest(self, tmp_path: Path) -> None:
        from cpc.config import load_manifest, save_manifest

        target = tmp_path / "project"
        target.mkdir()

        save_manifest(target, ["python-cli", "flutter-app"])
        manifest = load_manifest(target)

        assert manifest is not None
        assert manifest.profiles == ["python-cli", "flutter-app"]

    def test_load_legacy_single_profile_manifest(self, tmp_path: Path) -> None:
        """Old manifests with 'profile' string migrate to 'profiles' list."""
        import json

        target = tmp_path / "project"
        claude_dir = target / ".claude"
        claude_dir.mkdir(parents=True)

        # Write old-format manifest
        manifest_path = claude_dir / ".cpc.manifest.json"
        manifest_path.write_text(json.dumps({
            "source": "/some/path",
            "profile": "python-cli",
            "rules": ["universal-coding", "python-cli"],
            "skills": ["cpc-init"],
            "installed": "2026-01-01",
        }))

        from cpc.config import load_manifest
        manifest = load_manifest(target)

        assert manifest is not None
        assert manifest.profiles == ["python-cli"]

    def test_save_empty_profiles_deletes_manifest(self, tmp_path: Path) -> None:
        from cpc.config import load_manifest, save_manifest

        target = tmp_path / "project"
        target.mkdir()

        save_manifest(target, ["python-cli"])
        assert load_manifest(target) is not None

        save_manifest(target, [])
        assert load_manifest(target) is None
```

**Step 2: Run tests — verify they fail**

```bash
uv run pytest tests/test_linker.py::TestMultiProfileManifest -v
```

**Step 3: Update Manifest dataclass**

In `src/cpc/config.py`, replace the Manifest dataclass (lines 69-78):

```python
@dataclass(frozen=True)
class Manifest:
    """Recorded state of an installation, written to .cpc.manifest.json."""

    source: str
    profiles: list[str]
    installed: str
```

**Step 4: Update load_manifest**

Replace `load_manifest` (lines 114-132):

```python
def load_manifest(target: Path) -> Manifest | None:
    """Load .cpc.manifest.json from a target project."""
    manifest_path = target / ".claude" / MANIFEST_NAME
    # Fall back to legacy location for already-linked projects
    if not manifest_path.exists():
        legacy_path = target / ".claude" / "rules" / MANIFEST_NAME
        if legacy_path.exists():
            manifest_path = legacy_path
        else:
            return None
    with open(manifest_path) as f:
        raw = json.load(f)

    # Migrate legacy single-profile format
    if "profile" in raw and "profiles" not in raw:
        profiles = [raw["profile"]]
    else:
        profiles = raw.get("profiles", [])

    if not profiles:
        return None

    return Manifest(
        source=raw["source"],
        profiles=profiles,
        installed=raw.get("installed", ""),
    )
```

**Step 5: Update save_manifest**

Replace `save_manifest` (lines 135-152):

```python
def save_manifest(target: Path, profiles: list[str]) -> None:
    """Write .cpc.manifest.json to the target project.

    If profiles is empty, deletes the manifest (full uninstall).
    """
    manifest_path = target / ".claude" / MANIFEST_NAME
    # Clean up legacy location if it exists
    legacy_path = target / ".claude" / "rules" / MANIFEST_NAME
    if legacy_path.exists():
        legacy_path.unlink()

    if not profiles:
        if manifest_path.exists():
            manifest_path.unlink()
        return

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "source": str(REPO_ROOT),
        "profiles": profiles,
        "installed": str(__import__("datetime").date.today()),
    }
    with open(manifest_path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
```

**Step 6: Run the new tests**

```bash
uv run pytest tests/test_linker.py::TestMultiProfileManifest -v
```

Expected: 3 PASS

**Step 7: Fix existing tests that call save_manifest**

The existing tests don't call `save_manifest` directly, but the `install` and `update` click commands do. Those will be updated in later tasks. Verify existing tests still pass:

```bash
uv run pytest tests/test_linker.py -v
```

Any tests that call `save_manifest(target, profile)` with a Profile object will need updating — but since existing tests use `install_profile()` directly (not the click commands), they should still pass.

**Step 8: Commit**

```bash
git add src/cpc/config.py tests/test_linker.py
git commit -m "feat: multi-profile manifest format with legacy migration"
```

---

### Task 2: Add resolve_profiles helper

New function that computes the union of rules and skill dirs across multiple profile names.

**Files:**
- Modify: `src/cpc/config.py` (add `resolve_profiles` function after `discover_rules`)
- Test: `tests/test_linker.py`

**Step 1: Write test**

```python
class TestResolveProfiles:

    def test_union_of_two_profiles(self) -> None:
        from cpc.config import RuleSet, load_config, resolve_profiles

        config = load_config()
        rule_sets, skill_names = resolve_profiles(
            ["python-cli", "flutter-app"], config
        )

        # Both should contribute their rules
        assert RuleSet("universal-coding") in rule_sets
        assert RuleSet("python-cli") in rule_sets
        assert RuleSet("flutter-app") in rule_sets
        # No duplicates
        assert rule_sets.count(RuleSet("universal-coding")) == 1

        # Both should contribute their skills
        assert "cpc-audit" in skill_names
        assert "flutter-interface-design" in skill_names
        # No duplicates
        assert skill_names.count("cpc-audit") == 1

    def test_unknown_profile_errors(self) -> None:
        from cpc.config import load_config, resolve_profiles

        config = load_config()
        with pytest.raises(KeyError):
            resolve_profiles(["nonexistent"], config)
```

**Step 2: Run tests — verify they fail**

```bash
uv run pytest tests/test_linker.py::TestResolveProfiles -v
```

**Step 3: Implement resolve_profiles**

Add after `discover_rules` in `src/cpc/config.py`:

```python
def resolve_profiles(
    profile_names: list[str], config: Config
) -> tuple[list[RuleSet], list[str]]:
    """Compute the union of rules and skills across multiple profiles.

    Returns deduplicated lists preserving first-seen order.
    Raises KeyError if a profile name is not found in config.
    """
    seen_rules: dict[RuleSet, None] = {}
    seen_skills: dict[str, None] = {}

    for name in profile_names:
        profile = config.profiles[name]  # KeyError if missing
        for rule in profile.rules:
            seen_rules.setdefault(rule, None)
        for skill in profile.skills:
            seen_skills.setdefault(skill, None)

    return list(seen_rules), list(seen_skills)
```

**Step 4: Run tests**

```bash
uv run pytest tests/test_linker.py::TestResolveProfiles -v
```

Expected: 2 PASS

**Step 5: Commit**

```bash
git add src/cpc/config.py tests/test_linker.py
git commit -m "feat: add resolve_profiles helper for union computation"
```

---

### Task 3: Update install command to be additive

Change the `install` click command to load existing manifest, append the new profile, compute union, and sync.

**Files:**
- Modify: `src/cpc/linker.py:322-361` (install command)
- Modify: `src/cpc/linker.py:364-372` (_gitignore_from_profile → _gitignore_from_profiles)
- Modify: `src/cpc/linker.py:21-31` (imports — add resolve_profiles)
- Test: `tests/test_linker.py`

**Step 1: Write tests**

```python
class TestMultiProfileInstall:
    """Tests for additive multi-profile installation."""

    def test_additive_install(self, tmp_path: Path) -> None:
        """Installing a second profile keeps the first profile's symlinks."""
        from cpc.linker import install_profile

        rules_dir = _create_source_rules(tmp_path)
        target = _create_target(tmp_path)

        # Install universal (simulating python-cli's rules)
        install_profile(
            target=target,
            rule_sets=[UNIVERSAL],
            skill_dirs=[],
            rules_dir=rules_dir,
        )

        # Install union of both (simulating additive install)
        result = install_profile(
            target=target,
            rule_sets=[UNIVERSAL, TYPESCRIPT_WEB],
            skill_dirs=[],
            rules_dir=rules_dir,
        )

        rules = target / ".claude" / "rules"
        # Universal symlinks still present (updated)
        assert (rules / "universal-coding-review.md").is_symlink()
        # TypeScript symlinks added
        assert (rules / "typescript-web-types.md").is_symlink()
        assert len(result.cleaned) == 0

    def test_install_already_installed_profile_is_noop(self, tmp_path: Path) -> None:
        """Re-installing the same profile doesn't duplicate in manifest."""
        import json
        from cpc.config import save_manifest, load_manifest

        target = tmp_path / "project"
        target.mkdir()

        save_manifest(target, ["python-cli"])
        manifest = load_manifest(target)
        assert manifest is not None
        assert manifest.profiles == ["python-cli"]

        # Simulating what install command does: append if not present
        profiles = list(manifest.profiles)
        if "python-cli" not in profiles:
            profiles.append("python-cli")

        save_manifest(target, profiles)
        manifest = load_manifest(target)
        assert manifest is not None
        assert manifest.profiles == ["python-cli"]
```

**Step 2: Run tests — verify they pass (these test the logic, not the click command)**

```bash
uv run pytest tests/test_linker.py::TestMultiProfileInstall -v
```

**Step 3: Update imports in linker.py**

Add `resolve_profiles` to the import from `cpc.config`:

```python
from cpc.config import (
    RULES_DIR,
    Config,
    Profile,
    RuleSet,
    discover_rules,
    load_config,
    load_manifest,
    resolve_profiles,
    resolve_skill,
    save_manifest,
)
```

**Step 4: Replace _gitignore_from_profile with _gitignore_from_profiles**

```python
def _gitignore_from_profiles(
    target: Path, profile_names: list[str], config: Config
) -> None:
    """Update .gitignore with the union of files from all installed profiles."""
    rule_sets, skill_names = resolve_profiles(profile_names, config)
    discovered = discover_rules(rule_sets)
    rule_files = [f.name for files in discovered.values() for f in files]
    update_gitignore(
        target=target,
        rule_files=rule_files,
        skill_names=skill_names,
    )
```

**Step 5: Replace install command**

```python
@click.command()
@click.argument("target", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option(
    "--profile",
    "profile_name",
    default=None,
    type=click.Choice(list(load_config().profiles.keys()), case_sensitive=False),
    help="Profile to install (omit for interactive selection).",
)
def install(target: Path, profile_name: str | None) -> None:
    """Install rules and skills into a project (additive)."""
    target = target.resolve()
    config = load_config()

    if profile_name is not None:
        profile = config.profiles[profile_name]
    else:
        profile = _select_profile(config)

    # Load existing manifest and append new profile
    manifest = load_manifest(target)
    if manifest is not None:
        profiles = list(manifest.profiles)
    else:
        profiles = []

    if profile.name not in profiles:
        profiles.append(profile.name)

    # Compute union of all installed profiles
    union_rules, union_skill_names = resolve_profiles(profiles, config)

    # Resolve skill directories
    skill_dirs: list[Path] = []
    for skill_name in union_skill_names:
        skill_path = resolve_skill(skill_name, config.skill_sources)
        if skill_path is None:
            print_warning(f"Skill '{skill_name}' not found in any source.")
        else:
            skill_dirs.append(skill_path)

    result = install_profile(
        target=target,
        rule_sets=union_rules,
        skill_dirs=skill_dirs,
    )

    _print_result(result)
    save_manifest(target, profiles)
    _gitignore_from_profiles(target, profiles, config)
```

**Step 6: Run all tests**

```bash
uv run pytest tests/test_linker.py -v
```

**Step 7: Commit**

```bash
git add src/cpc/linker.py tests/test_linker.py
git commit -m "feat: make install additive with multi-profile union"
```

---

### Task 4: Update the update command

Change `update` to iterate all installed profiles from the manifest.

**Files:**
- Modify: `src/cpc/linker.py:375-427` (update command)

**Step 1: Replace update command**

```python
@click.command()
@click.argument("target", type=click.Path(exists=True, file_okay=False, path_type=Path))
def update(target: Path) -> None:
    """Re-apply all installed profiles and refresh skill sources."""
    target = target.resolve()
    manifest = load_manifest(target)

    if manifest is None:
        print_error(f"No installation found in {target}. Run 'install' first.")
        raise SystemExit(1)

    config = load_config()

    # Validate all profiles still exist
    for name in manifest.profiles:
        if name not in config.profiles:
            print_error(f"Profile '{name}' no longer exists in config.")
            raise SystemExit(1)

    # Run source update commands
    for source in config.skill_sources:
        if source.update and source.path.is_dir():
            console.print(f"  Updating {source.path.name}...")
            proc = subprocess.run(
                source.update,
                shell=True,
                cwd=source.path,
                check=False,
                capture_output=True,
                text=True,
            )
            if proc.returncode != 0:
                console.print(f"  [warning]Update failed (exit {proc.returncode})[/]")
                if proc.stderr:
                    console.print(f"  [warning]{proc.stderr.strip()}[/]")

    # Compute union and sync
    union_rules, union_skill_names = resolve_profiles(manifest.profiles, config)

    skill_dirs: list[Path] = []
    for skill_name in union_skill_names:
        skill_path = resolve_skill(skill_name, config.skill_sources)
        if skill_path is not None:
            skill_dirs.append(skill_path)

    result = install_profile(
        target=target,
        rule_sets=union_rules,
        skill_dirs=skill_dirs,
    )

    _print_result(result)
    save_manifest(target, manifest.profiles)
    _gitignore_from_profiles(target, manifest.profiles, config)
```

**Step 2: Run all tests**

```bash
uv run pytest -v
```

**Step 3: Commit**

```bash
git add src/cpc/linker.py
git commit -m "feat: update command re-syncs all installed profiles"
```

---

### Task 5: Add uninstall command

New click command that removes one profile and syncs to the reduced union.

**Files:**
- Modify: `src/cpc/linker.py` (add uninstall command)
- Modify: `src/cpc/cli.py` (register uninstall command)
- Test: `tests/test_linker.py`

**Step 1: Write tests**

```python
class TestMultiProfileUninstall:

    def test_uninstall_one_of_two_profiles(self, tmp_path: Path) -> None:
        """Uninstalling one profile keeps the other's symlinks."""
        from cpc.linker import install_profile

        rules_dir = _create_source_rules(tmp_path)
        target = _create_target(tmp_path)

        # Install both profiles' rules (union)
        install_profile(
            target=target,
            rule_sets=[UNIVERSAL, TYPESCRIPT_WEB],
            skill_dirs=[],
            rules_dir=rules_dir,
        )

        # Now sync with only UNIVERSAL (simulating uninstall of typescript-web)
        result = install_profile(
            target=target,
            rule_sets=[UNIVERSAL],
            skill_dirs=[],
            rules_dir=rules_dir,
        )

        rules = target / ".claude" / "rules"
        assert (rules / "universal-coding-review.md").is_symlink()
        assert not (rules / "typescript-web-types.md").exists()
        assert len(result.cleaned) == 1

    def test_uninstall_last_profile_cleans_everything(self, tmp_path: Path) -> None:
        """Uninstalling the last profile removes all symlinks and manifest."""
        from cpc.config import load_manifest, save_manifest
        from cpc.linker import install_profile

        rules_dir = _create_source_rules(tmp_path)
        target = _create_target(tmp_path)

        install_profile(
            target=target,
            rule_sets=[UNIVERSAL],
            skill_dirs=[],
            rules_dir=rules_dir,
        )
        save_manifest(target, ["python-cli"])

        # Sync with empty sets (simulating uninstall of last profile)
        result = install_profile(
            target=target,
            rule_sets=[],
            skill_dirs=[],
            rules_dir=rules_dir,
        )

        save_manifest(target, [])
        assert load_manifest(target) is None
        assert len(result.cleaned) == 2  # both universal-coding files

    def test_uninstall_nonexistent_profile_manifest(self, tmp_path: Path) -> None:
        """Uninstalling a profile not in the manifest is an error."""
        from cpc.config import save_manifest, load_manifest

        target = tmp_path / "project"
        target.mkdir()

        save_manifest(target, ["python-cli"])
        manifest = load_manifest(target)
        assert manifest is not None
        assert "flutter-app" not in manifest.profiles
```

**Step 2: Run tests — verify they pass**

```bash
uv run pytest tests/test_linker.py::TestMultiProfileUninstall -v
```

These test the underlying logic. The click command test will be manual.

**Step 3: Add uninstall command to linker.py**

Add after the `update` command:

```python
@click.command()
@click.argument("target", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option(
    "--profile",
    "profile_name",
    required=True,
    help="Profile to uninstall.",
)
def uninstall(target: Path, profile_name: str) -> None:
    """Remove a profile and clean up its unique symlinks."""
    target = target.resolve()
    manifest = load_manifest(target)

    if manifest is None:
        print_error(f"No installation found in {target}.")
        raise SystemExit(1)

    if profile_name not in manifest.profiles:
        print_error(
            f"Profile '{profile_name}' is not installed. "
            f"Installed: {', '.join(manifest.profiles)}"
        )
        raise SystemExit(1)

    config = load_config()
    remaining = [p for p in manifest.profiles if p != profile_name]

    if remaining:
        # Compute union of remaining profiles and sync
        union_rules, union_skill_names = resolve_profiles(remaining, config)

        skill_dirs: list[Path] = []
        for skill_name in union_skill_names:
            skill_path = resolve_skill(skill_name, config.skill_sources)
            if skill_path is not None:
                skill_dirs.append(skill_path)

        result = install_profile(
            target=target,
            rule_sets=union_rules,
            skill_dirs=skill_dirs,
        )

        _print_result(result)
        save_manifest(target, remaining)
        _gitignore_from_profiles(target, remaining, config)
    else:
        # Last profile — clean everything
        result = install_profile(
            target=target,
            rule_sets=[],
            skill_dirs=[],
        )

        _print_result(result)
        save_manifest(target, [])
        _clean_gitignore(target)

    console.print(f"  Uninstalled [label]{profile_name}[/]")
```

**Step 4: Add _clean_gitignore helper**

Add after `update_gitignore` in `linker.py`:

```python
def _clean_gitignore(target: Path) -> None:
    """Remove the cpc-managed section from .gitignore."""
    gitignore_path = target / ".gitignore"
    if not gitignore_path.exists():
        return
    content = gitignore_path.read_text()
    if _CPC_START not in content:
        return
    start_idx = content.index(_CPC_START)
    end_idx = content.index(_CPC_END) + len(_CPC_END)
    if end_idx < len(content) and content[end_idx] == "\n":
        end_idx += 1
    # Also remove a leading blank line if present
    if start_idx > 0 and content[start_idx - 1] == "\n":
        start_idx -= 1
    content = content[:start_idx] + content[end_idx:]
    if content.strip():
        gitignore_path.write_text(content)
    else:
        gitignore_path.unlink()
```

**Step 5: Register uninstall in cli.py**

In `src/cpc/cli.py`, add to imports:

```python
from cpc.linker import install, uninstall, update
```

And add:

```python
main.add_command(uninstall)
```

**Step 6: Run all tests**

```bash
uv run pytest -v
```

**Step 7: Commit**

```bash
git add src/cpc/linker.py src/cpc/cli.py tests/test_linker.py
git commit -m "feat: add uninstall command for per-profile removal"
```

---

### Task 6: Update status command

The `status` command currently displays a single profile. Update to show all installed profiles and derive rules/skills from config.

**Files:**
- Modify: `src/cpc/config.py:183-222` (status command)

**Step 1: Replace status command**

```python
@click.command()
@click.argument("target", type=click.Path(exists=True, file_okay=False, path_type=Path))
def status(target: Path) -> None:
    """Show installed profiles, rule sets, skills, and symlink health."""
    target = target.resolve()
    manifest = load_manifest(target)

    if manifest is None:
        print_error(f"No installation found in {target}")
        raise SystemExit(1)

    config = load_config()
    console.print(f"\n[label]Profiles:[/]  {', '.join(manifest.profiles)}")
    console.print(f"[label]Source:[/]    {manifest.source}")
    console.print(f"[label]Installed:[/] {manifest.installed}")

    # Derive rules and skills from config
    try:
        union_rules, union_skills = resolve_profiles(manifest.profiles, config)
        console.print(f"\n[label]Rule sets:[/] {', '.join(union_rules)}")
        if union_skills:
            console.print(f"[label]Skills:[/]    {', '.join(union_skills)}")
        else:
            console.print("[label]Skills:[/]    (none)")
    except KeyError as e:
        print_warning(f"Profile {e} no longer exists in config. Run 'cpc update'.")

    # Check symlink health
    rules_dir = target / ".claude" / "rules"
    skills_dir = target / ".claude" / "skills"
    broken: list[str] = []

    for check_dir in [rules_dir, skills_dir]:
        if not check_dir.exists():
            continue
        for entry in check_dir.iterdir():
            if entry.is_symlink() and not entry.resolve().exists():
                broken.append(str(entry.relative_to(target)))

    if broken:
        console.print(f"\n[warning]Broken symlinks ({len(broken)}):[/]")
        for b in broken:
            console.print(f"  [error]✗[/] {b}")
    else:
        console.print("\n[success]All symlinks healthy.[/]")
    console.print()
```

**Step 2: Add `resolve_profiles` to status imports**

The status command is in `config.py`. Add `resolve_profiles` to the function's scope — it's already defined in the same file, so no import needed. But make sure `load_config` is available (it is — same file).

**Step 3: Run all tests**

```bash
uv run pytest -v
```

**Step 4: Commit**

```bash
git add src/cpc/config.py
git commit -m "feat: status command shows all installed profiles"
```

---

### Task 7: Remove unused Profile import from linker.py

After the refactor, `linker.py` no longer needs to import `Profile` from config (it passes profile names as strings now).

**Files:**
- Modify: `src/cpc/linker.py:21-31` (imports)

**Step 1: Remove `Profile` from the import list**

Remove `Profile` from the import block — it's no longer referenced anywhere in linker.py.

**Step 2: Run all tests**

```bash
uv run pytest -v
```

**Step 3: Commit**

```bash
git add src/cpc/linker.py
git commit -m "chore: remove unused Profile import from linker"
```

---

### Task 8: Final verification

**Step 1: Run full test suite**

```bash
uv run pytest -v
```

Expected: All tests pass.

**Step 2: Verify no regressions manually (optional)**

```bash
uv run cpc install --help
uv run cpc uninstall --help
uv run cpc update --help
```

---

## Parallelization

- **Task 1** must be first (foundation)
- **Task 2** depends on Task 1 (uses new Manifest)
- **Tasks 3-5** depend on Task 2 (use resolve_profiles) but are independent of each other
- **Task 6** depends on Task 1-2 (uses new Manifest + resolve_profiles)
- **Task 7** depends on Tasks 3-5 (cleanup after refactor)
- **Task 8** depends on all
