# CLI Refactor Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Refactor `install.py` into a `uv`-managed `click` + `rich` CLI with declarative YAML profiles, skills support, and safety-tested filesystem operations.

**Architecture:** Python package (`src/cpc/`) with co-located click commands. Config loaded from `config.yaml` into frozen dataclasses. All filesystem mutation in `linker.py`, tested against real `tmp_path` fixtures. Entry point via `[project.scripts]` so `uv run cpc` works.

**Tech Stack:** Python 3.11+, click, rich, pyyaml, pytest, uv

---

### Task 1: Project scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `src/cpc/__init__.py`
- Create: `src/cpc/cli.py` (stub)

**Step 1: Create `pyproject.toml`**

```toml
[project]
name = "cpc"
version = "0.1.0"
description = "Manage shared Claude Code rules and skills across projects"
requires-python = ">=3.11"
dependencies = [
    "click>=8.1",
    "rich>=13.0",
    "pyyaml>=6.0",
]

[project.scripts]
cpc = "cpc.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/cpc"]

[tool.pytest.ini_options]
testpaths = ["tests"]

[dependency-groups]
dev = [
    "pytest>=8.0",
]
```

**Step 2: Create `src/cpc/__init__.py`**

```python
"""CPC — Claude Project Context manager."""
```

**Step 3: Create stub `src/cpc/cli.py`**

```python
"""CLI entry point — assembles click group from submodules."""

import click


@click.group()
def main() -> None:
    """Manage Claude Code rules and skills across projects."""


if __name__ == "__main__":
    main()
```

**Step 4: Verify uv resolves the package**

Run: `uv run cpc --help`
Expected: Shows help text with "Manage Claude Code rules and skills across projects."

**Step 5: Commit**

```bash
git add pyproject.toml src/
git commit -m "feat: scaffold uv-managed cpc package with click entry point"
```

---

### Task 2: Console module

**Files:**
- Create: `src/cpc/console.py`

**Step 1: Write `console.py`**

This wraps `rich.console.Console` for consistent output across all commands.

```python
"""Rich console wrapper for consistent CLI output."""

from rich.console import Console
from rich.table import Table
from rich.theme import Theme

theme = Theme(
    {
        "info": "cyan",
        "success": "green",
        "warning": "yellow",
        "error": "red bold",
        "path": "blue underline",
        "label": "bold",
    }
)

console = Console(theme=theme)


def print_linked(filename: str) -> None:
    console.print(f"  [success]+[/] {filename}")


def print_updated(filename: str) -> None:
    console.print(f"  [info]~[/] {filename}")


def print_skipped(filename: str) -> None:
    console.print(f"  [warning]![/] {filename} [warning](local override)[/]")


def print_cleaned(filename: str) -> None:
    console.print(f"  [error]-[/] {filename}")


def print_error(message: str) -> None:
    console.print(f"[error]Error:[/] {message}", style="error")


def print_heading(text: str) -> None:
    console.print(f"\n[label]{text}[/]")


def print_rule() -> None:
    console.rule()
```

**Step 2: Verify import works**

Run: `uv run python -c "from cpc.console import console; console.print('[success]ok[/]')"`
Expected: Prints "ok" in green.

**Step 3: Commit**

```bash
git add src/cpc/console.py
git commit -m "feat: add rich console wrapper for CLI output"
```

---

### Task 3: Config types and loader

**Files:**
- Create: `src/cpc/config.py`
- Create: `config.yaml`

**Step 1: Write `config.py` with types and loader**

```python
"""Config loading, types, and the `status` command."""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

import click
import yaml

from cpc.console import console, print_error

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RULES_DIR = REPO_ROOT / "rules"
MANIFEST_NAME = ".manifest.json"


# ── Types ──────────────────────────────────────────────────────────


class RuleSet(StrEnum):
    """Available rule set names, matching rules/ subdirectories."""

    UNIVERSAL = "universal"
    TYPESCRIPT_WEB = "typescript-web"
    ASTRO = "astro"
    NEXTJS = "nextjs"


@dataclass(frozen=True)
class SkillSource:
    """A directory that contains skills."""

    path: Path
    update: str | None = None


@dataclass(frozen=True)
class Profile:
    """A named combination of rule sets and skills for a project type."""

    name: str
    rules: list[RuleSet]
    skills: list[str]


@dataclass(frozen=True)
class Config:
    """Top-level config parsed from config.yaml."""

    skill_sources: list[SkillSource]
    profiles: dict[str, Profile]


@dataclass(frozen=True)
class Manifest:
    """Recorded state of an installation, written to .manifest.json."""

    source: str
    profile: str
    rules: list[str]
    skills: list[str]
    installed: str


# ── Loading ────────────────────────────────────────────────────────


def load_config(config_path: Path | None = None) -> Config:
    """Parse config.yaml into a Config dataclass."""
    if config_path is None:
        config_path = REPO_ROOT / "config.yaml"

    with open(config_path) as f:
        raw = yaml.safe_load(f)

    skill_sources: list[SkillSource] = []
    for entry in raw.get("sources", {}).get("skills", []):
        path = Path(entry["path"])
        if not path.is_absolute():
            path = (REPO_ROOT / path).resolve()
        skill_sources.append(
            SkillSource(path=path, update=entry.get("update"))
        )

    profiles: dict[str, Profile] = {}
    for name, data in raw.get("profiles", {}).items():
        rules = [RuleSet(r) for r in data.get("rules", [])]
        skills = data.get("skills", [])
        profiles[name] = Profile(name=name, rules=rules, skills=skills)

    return Config(skill_sources=skill_sources, profiles=profiles)


def load_manifest(target: Path) -> Manifest | None:
    """Load .manifest.json from a target project."""
    manifest_path = target / ".claude" / "rules" / MANIFEST_NAME
    if not manifest_path.exists():
        return None
    with open(manifest_path) as f:
        raw = json.load(f)
    return Manifest(
        source=raw["source"],
        profile=raw["profile"],
        rules=raw.get("rules", []),
        skills=raw.get("skills", []),
        installed=raw.get("installed", ""),
    )


def save_manifest(target: Path, profile: Profile) -> None:
    """Write .manifest.json to the target project."""
    manifest_path = target / ".claude" / "rules" / MANIFEST_NAME
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "source": str(REPO_ROOT),
        "profile": profile.name,
        "rules": [str(r) for r in profile.rules],
        "skills": profile.skills,
        "installed": str(__import__("datetime").date.today()),
    }
    with open(manifest_path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def resolve_skill(name: str, sources: list[SkillSource]) -> Path | None:
    """Find a skill directory by name across all sources. First match wins."""
    for source in sources:
        if not source.path.is_dir():
            continue
        for entry in source.path.iterdir():
            if entry.is_dir() and entry.name.lower().replace("-", "").replace("_", "") == name.lower().replace("-", "").replace("_", ""):
                # Verify it has a SKILL.md
                if (entry / "SKILL.md").exists():
                    return entry
    return None


def discover_rules(rule_sets: list[RuleSet]) -> dict[RuleSet, list[Path]]:
    """Find all .md files for the given rule sets."""
    result: dict[RuleSet, list[Path]] = {}
    for rule_set in rule_sets:
        set_dir = RULES_DIR / rule_set.value
        if set_dir.is_dir():
            result[rule_set] = sorted(set_dir.glob("*.md"))
        else:
            result[rule_set] = []
    return result


# ── Status command ─────────────────────────────────────────────────


@click.command()
@click.argument("target", type=click.Path(exists=True, file_okay=False, path_type=Path))
def status(target: Path) -> None:
    """Show what's installed in a project."""
    target = target.resolve()
    manifest = load_manifest(target)

    if manifest is None:
        print_error(f"No installation found in {target}")
        raise SystemExit(1)

    console.print(f"\n[label]Profile:[/]  {manifest.profile}")
    console.print(f"[label]Source:[/]   {manifest.source}")
    console.print(f"[label]Installed:[/] {manifest.installed}")

    console.print(f"\n[label]Rule sets:[/] {', '.join(manifest.rules)}")
    if manifest.skills:
        console.print(f"[label]Skills:[/]    {', '.join(manifest.skills)}")
    else:
        console.print("[label]Skills:[/]    (none)")

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

**Step 2: Write `config.yaml`**

```yaml
sources:
  skills:
    - path: skills/
    - path: ../claude-skills
      update: git -C ../claude-skills pull

profiles:
  astro:
    rules:
      - universal
      - typescript-web
      - astro
    skills:
      - vibesec

  nextjs:
    rules:
      - universal
      - typescript-web
      - nextjs
    skills:
      - vibesec
```

**Step 3: Verify config loads**

Run: `uv run python -c "from cpc.config import load_config; c = load_config(); print(c.profiles.keys())"`
Expected: `dict_keys(['astro', 'nextjs'])`

**Step 4: Commit**

```bash
git add src/cpc/config.py config.yaml
git commit -m "feat: add config types, YAML loader, and status command"
```

---

### Task 4: Linker — safety-critical tests first

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/test_linker.py` (safety tests only — no implementation yet)

**Step 1: Write safety invariant tests**

These tests define the contract before we write the code. They use `tmp_path`
to create realistic filesystem layouts.

```python
"""Safety-critical tests for the linker module.

These tests verify that the linker NEVER performs destructive operations
on non-symlink files. If any of these fail, the tool is dangerous.
"""

from pathlib import Path

import pytest


def _create_source_rules(tmp_path: Path) -> Path:
    """Create a fake rules/ directory with two sets."""
    rules = tmp_path / "rules"
    universal = rules / "universal"
    universal.mkdir(parents=True)
    (universal / "universal-review.md").write_text("# Review")
    (universal / "universal-security.md").write_text("# Security")

    ts = rules / "typescript-web"
    ts.mkdir(parents=True)
    (ts / "typescript-web-types.md").write_text("# Types")
    return rules


def _create_source_skills(tmp_path: Path) -> Path:
    """Create a fake skills/ directory with one skill."""
    skills = tmp_path / "skills"
    vibesec = skills / "vibesec"
    vibesec.mkdir(parents=True)
    (vibesec / "SKILL.md").write_text("# VibeSec")
    return skills


def _create_target(tmp_path: Path) -> Path:
    """Create a fake target project directory."""
    target = tmp_path / "project"
    target.mkdir()
    return target


class TestSafetyInvariants:
    """If any of these tests fail, the tool is dangerous."""

    def test_never_deletes_non_symlink_files(self, tmp_path: Path) -> None:
        """A real file in .claude/rules/ must survive install — it's a local override."""
        from cpc.linker import install_profile
        from cpc.config import RuleSet

        rules_dir = _create_source_rules(tmp_path)
        target = _create_target(tmp_path)

        # Pre-create a local override file (not a symlink)
        claude_rules = target / ".claude" / "rules"
        claude_rules.mkdir(parents=True)
        local_file = claude_rules / "universal-review.md"
        local_file.write_text("# My local override")

        install_profile(
            target=target,
            rule_sets=[RuleSet.UNIVERSAL],
            skill_dirs=[],
            rules_dir=rules_dir,
        )

        # Local file must still exist with original content
        assert local_file.exists()
        assert not local_file.is_symlink()
        assert local_file.read_text() == "# My local override"

    def test_never_overwrites_non_symlink_files(self, tmp_path: Path) -> None:
        """Install must not replace a real file with a symlink."""
        from cpc.linker import install_profile
        from cpc.config import RuleSet

        rules_dir = _create_source_rules(tmp_path)
        target = _create_target(tmp_path)

        claude_rules = target / ".claude" / "rules"
        claude_rules.mkdir(parents=True)
        local_file = claude_rules / "universal-security.md"
        local_file.write_text("# Local security rules")

        install_profile(
            target=target,
            rule_sets=[RuleSet.UNIVERSAL],
            skill_dirs=[],
            rules_dir=rules_dir,
        )

        assert not local_file.is_symlink()
        assert local_file.read_text() == "# Local security rules"

    def test_stale_cleanup_only_removes_our_symlinks(self, tmp_path: Path) -> None:
        """Cleanup must not touch symlinks that point outside our sources."""
        from cpc.linker import install_profile
        from cpc.config import RuleSet

        rules_dir = _create_source_rules(tmp_path)
        target = _create_target(tmp_path)

        # Create a symlink from another tool
        claude_rules = target / ".claude" / "rules"
        claude_rules.mkdir(parents=True)
        other_source = tmp_path / "other-tool" / "some-rule.md"
        other_source.parent.mkdir(parents=True)
        other_source.write_text("# Other tool's rule")
        foreign_link = claude_rules / "some-rule.md"
        foreign_link.symlink_to(other_source)

        install_profile(
            target=target,
            rule_sets=[RuleSet.UNIVERSAL],
            skill_dirs=[],
            rules_dir=rules_dir,
        )

        # Foreign symlink must survive
        assert foreign_link.is_symlink()
        assert foreign_link.resolve() == other_source.resolve()

    def test_only_writes_inside_claude_directory(self, tmp_path: Path) -> None:
        """No files should be created outside .claude/ in the target."""
        from cpc.linker import install_profile
        from cpc.config import RuleSet

        rules_dir = _create_source_rules(tmp_path)
        skills_dir = _create_source_skills(tmp_path)
        target = _create_target(tmp_path)

        # Record files before install
        before = set()
        for p in target.rglob("*"):
            before.add(p)

        install_profile(
            target=target,
            rule_sets=[RuleSet.UNIVERSAL, RuleSet.TYPESCRIPT_WEB],
            skill_dirs=[(skills_dir / "vibesec")],
            rules_dir=rules_dir,
        )

        # All new files must be under .claude/
        for p in target.rglob("*"):
            if p not in before:
                rel = p.relative_to(target)
                assert rel.parts[0] == ".claude", f"File created outside .claude/: {rel}"


class TestCorrectBehavior:

    def test_creates_symlinks_for_selected_rules(self, tmp_path: Path) -> None:
        from cpc.linker import install_profile
        from cpc.config import RuleSet

        rules_dir = _create_source_rules(tmp_path)
        target = _create_target(tmp_path)

        result = install_profile(
            target=target,
            rule_sets=[RuleSet.UNIVERSAL],
            skill_dirs=[],
            rules_dir=rules_dir,
        )

        rules = target / ".claude" / "rules"
        link = rules / "universal-review.md"
        assert link.is_symlink()
        assert link.resolve().name == "universal-review.md"
        assert len(result.linked) == 2

    def test_creates_symlinks_for_selected_skills(self, tmp_path: Path) -> None:
        from cpc.linker import install_profile
        from cpc.config import RuleSet

        rules_dir = _create_source_rules(tmp_path)
        skills_dir = _create_source_skills(tmp_path)
        target = _create_target(tmp_path)

        result = install_profile(
            target=target,
            rule_sets=[],
            skill_dirs=[(skills_dir / "vibesec")],
            rules_dir=rules_dir,
        )

        skills = target / ".claude" / "skills"
        link = skills / "vibesec"
        assert link.is_symlink()
        assert (link / "SKILL.md").exists()

    def test_replaces_existing_symlinks(self, tmp_path: Path) -> None:
        from cpc.linker import install_profile
        from cpc.config import RuleSet

        rules_dir = _create_source_rules(tmp_path)
        target = _create_target(tmp_path)

        # Install twice
        install_profile(
            target=target, rule_sets=[RuleSet.UNIVERSAL],
            skill_dirs=[], rules_dir=rules_dir,
        )
        result = install_profile(
            target=target, rule_sets=[RuleSet.UNIVERSAL],
            skill_dirs=[], rules_dir=rules_dir,
        )

        assert len(result.updated) == 2
        assert len(result.linked) == 0

    def test_cleans_stale_symlinks_on_update(self, tmp_path: Path) -> None:
        from cpc.linker import install_profile
        from cpc.config import RuleSet

        rules_dir = _create_source_rules(tmp_path)
        target = _create_target(tmp_path)

        # Install universal + typescript-web
        install_profile(
            target=target,
            rule_sets=[RuleSet.UNIVERSAL, RuleSet.TYPESCRIPT_WEB],
            skill_dirs=[], rules_dir=rules_dir,
        )

        # Re-install with only universal — typescript-web links should be cleaned
        result = install_profile(
            target=target,
            rule_sets=[RuleSet.UNIVERSAL],
            skill_dirs=[], rules_dir=rules_dir,
        )

        assert len(result.cleaned) == 1  # typescript-web-types.md
        rules = target / ".claude" / "rules"
        assert not (rules / "typescript-web-types.md").exists()

    def test_idempotent_reinstall(self, tmp_path: Path) -> None:
        from cpc.linker import install_profile
        from cpc.config import RuleSet

        rules_dir = _create_source_rules(tmp_path)
        target = _create_target(tmp_path)

        sets = [RuleSet.UNIVERSAL, RuleSet.TYPESCRIPT_WEB]

        result1 = install_profile(
            target=target, rule_sets=sets,
            skill_dirs=[], rules_dir=rules_dir,
        )
        result2 = install_profile(
            target=target, rule_sets=sets,
            skill_dirs=[], rules_dir=rules_dir,
        )

        # Same number of active symlinks, no cleaned, no skipped
        active1 = len(result1.linked) + len(result1.updated)
        active2 = len(result2.linked) + len(result2.updated)
        assert active1 == active2
        assert len(result2.cleaned) == 0


class TestErrorHandling:

    def test_nonexistent_profile_errors(self, tmp_path: Path) -> None:
        from cpc.config import load_config

        config_path = tmp_path / "config.yaml"
        config_path.write_text("profiles: {}\nsources:\n  skills: []\n")
        config = load_config(config_path)
        assert "nonexistent" not in config.profiles

    def test_missing_manifest_on_update_errors(self, tmp_path: Path) -> None:
        from cpc.config import load_manifest

        target = tmp_path / "project"
        target.mkdir()
        assert load_manifest(target) is None
```

**Step 2: Create empty `tests/__init__.py`**

```python
```

**Step 3: Run tests to verify they fail (TDD red phase)**

Run: `uv run pytest tests/test_linker.py -v`
Expected: All tests FAIL with `ImportError: cannot import name 'install_profile' from 'cpc.linker'`

**Step 4: Commit**

```bash
git add tests/
git commit -m "test: add safety invariant and behavior tests for linker (red)"
```

---

### Task 5: Linker implementation

**Files:**
- Create: `src/cpc/linker.py`

**Step 1: Write `linker.py` with types, core logic, and click commands**

```python
"""Symlink logic and install/update CLI commands."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

import click

from cpc.config import (
    MANIFEST_NAME,
    RULES_DIR,
    Config,
    Profile,
    RuleSet,
    discover_rules,
    load_config,
    load_manifest,
    resolve_skill,
    save_manifest,
)
from cpc.console import (
    console,
    print_cleaned,
    print_error,
    print_heading,
    print_linked,
    print_rule,
    print_skipped,
    print_updated,
)


# ── Result types ───────────────────────────────────────────────────


class LinkAction(StrEnum):
    """What happened to a single file during install."""

    LINKED = "linked"
    UPDATED = "updated"
    SKIPPED = "skipped"
    CLEANED = "cleaned"


@dataclass(frozen=True)
class LinkResult:
    """Outcome for a single file."""

    filename: str
    action: LinkAction
    target: Path | None = None


@dataclass(frozen=True)
class InstallResult:
    """Full outcome of an install or update operation."""

    target_dir: Path
    profile: str
    results: list[LinkResult]

    @property
    def linked(self) -> list[LinkResult]:
        return [r for r in self.results if r.action == LinkAction.LINKED]

    @property
    def updated(self) -> list[LinkResult]:
        return [r for r in self.results if r.action == LinkAction.UPDATED]

    @property
    def skipped(self) -> list[LinkResult]:
        return [r for r in self.results if r.action == LinkAction.SKIPPED]

    @property
    def cleaned(self) -> list[LinkResult]:
        return [r for r in self.results if r.action == LinkAction.CLEANED]


# ── Core logic ─────────────────────────────────────────────────────


def install_profile(
    *,
    target: Path,
    rule_sets: list[RuleSet],
    skill_dirs: list[Path],
    rules_dir: Path = RULES_DIR,
) -> InstallResult:
    """Symlink rules and skills into a target project. Returns structured result."""
    results: list[LinkResult] = []

    rules_target = target / ".claude" / "rules"
    rules_target.mkdir(parents=True, exist_ok=True)

    # ── Determine expected rule symlinks ──
    discovered = discover_rules(rule_sets, rules_dir=rules_dir)
    expected_rule_names: set[str] = set()
    for files in discovered.values():
        for f in files:
            expected_rule_names.add(f.name)

    # ── Clean stale rule symlinks ──
    for existing in rules_target.iterdir():
        if existing.name == MANIFEST_NAME:
            continue
        if existing.is_symlink():
            link_target = existing.resolve()
            # Only clean symlinks that point into OUR rules directory
            try:
                link_target.relative_to(rules_dir.resolve())
            except ValueError:
                continue  # Foreign symlink — leave it alone
            if existing.name not in expected_rule_names:
                existing.unlink()
                results.append(LinkResult(existing.name, LinkAction.CLEANED))

    # ── Install rule symlinks ──
    for rule_set, files in discovered.items():
        for src_file in files:
            dest = rules_target / src_file.name
            rel_source = os.path.relpath(src_file, rules_target)

            if dest.exists() or dest.is_symlink():
                if dest.is_symlink():
                    dest.unlink()
                    dest.symlink_to(rel_source)
                    results.append(LinkResult(src_file.name, LinkAction.UPDATED, src_file))
                else:
                    results.append(LinkResult(src_file.name, LinkAction.SKIPPED))
            else:
                dest.symlink_to(rel_source)
                results.append(LinkResult(src_file.name, LinkAction.LINKED, src_file))

    # ── Install skill symlinks ──
    if skill_dirs:
        skills_target = target / ".claude" / "skills"
        skills_target.mkdir(parents=True, exist_ok=True)

        expected_skill_names: set[str] = {d.name for d in skill_dirs}

        # Clean stale skill symlinks
        for existing in skills_target.iterdir():
            if existing.is_symlink():
                link_target = existing.resolve()
                # Only clean if it's a known skill source
                if existing.name not in expected_skill_names:
                    # Check if it points to one of our source directories
                    for sd in skill_dirs:
                        try:
                            link_target.relative_to(sd.parent.resolve())
                            existing.unlink()
                            results.append(LinkResult(existing.name, LinkAction.CLEANED))
                            break
                        except ValueError:
                            continue

        for skill_dir in skill_dirs:
            dest = skills_target / skill_dir.name
            rel_source = os.path.relpath(skill_dir, skills_target)

            if dest.exists() or dest.is_symlink():
                if dest.is_symlink():
                    dest.unlink()
                    dest.symlink_to(rel_source)
                    results.append(LinkResult(skill_dir.name, LinkAction.UPDATED, skill_dir))
                else:
                    results.append(LinkResult(skill_dir.name, LinkAction.SKIPPED))
            else:
                dest.symlink_to(rel_source)
                results.append(LinkResult(skill_dir.name, LinkAction.LINKED, skill_dir))

    return InstallResult(
        target_dir=target / ".claude",
        profile="",  # Set by caller
        results=results,
    )


def _print_result(result: InstallResult) -> None:
    """Display install result using rich console."""
    print_rule()

    if result.linked:
        print_heading(f"Linked ({len(result.linked)})")
        for r in result.linked:
            print_linked(r.filename)

    if result.updated:
        print_heading(f"Updated ({len(result.updated)})")
        for r in result.updated:
            print_updated(r.filename)

    if result.skipped:
        print_heading(f"Skipped — local override ({len(result.skipped)})")
        for r in result.skipped:
            print_skipped(r.filename)

    if result.cleaned:
        print_heading(f"Cleaned — stale ({len(result.cleaned)})")
        for r in result.cleaned:
            print_cleaned(r.filename)

    total = len(result.linked) + len(result.updated)
    console.print(f"\n  Active symlinks: [success]{total}[/]")
    if result.skipped:
        console.print(f"  Local overrides: [warning]{len(result.skipped)}[/]")
    console.print()


def _select_profile(config: Config) -> Profile:
    """Interactive profile selection."""
    names = list(config.profiles.keys())
    console.print("\n[label]Available profiles:[/]\n")
    for i, name in enumerate(names, 1):
        profile = config.profiles[name]
        rules_str = ", ".join(str(r) for r in profile.rules)
        skills_str = ", ".join(profile.skills) if profile.skills else "(none)"
        console.print(f"  [label]{i}.[/] {name}")
        console.print(f"     Rules:  {rules_str}")
        console.print(f"     Skills: {skills_str}")
        console.print()

    while True:
        choice = click.prompt("Select profile number", type=int)
        if 1 <= choice <= len(names):
            return config.profiles[names[choice - 1]]
        console.print("[warning]Invalid selection. Try again.[/]")


# ── CLI commands ───────────────────────────────────────────────────


@click.command()
@click.argument("target", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--profile", "profile_name", default=None, help="Profile name (non-interactive).")
def install(target: Path, profile_name: str | None) -> None:
    """Install rules and skills into a project."""
    target = target.resolve()
    config = load_config()

    if profile_name:
        if profile_name not in config.profiles:
            print_error(f"Unknown profile: {profile_name}")
            print_error(f"Available: {', '.join(config.profiles.keys())}")
            raise SystemExit(1)
        profile = config.profiles[profile_name]
    else:
        profile = _select_profile(config)

    console.print(f"\nInstalling profile [label]{profile.name}[/] into [path]{target}[/]")

    # Resolve skills
    skill_dirs: list[Path] = []
    for skill_name in profile.skills:
        resolved = resolve_skill(skill_name, config.skill_sources)
        if resolved:
            skill_dirs.append(resolved)
        else:
            console.print(f"[warning]Skill not found: {skill_name}[/]")

    result = install_profile(
        target=target,
        rule_sets=profile.rules,
        skill_dirs=skill_dirs,
    )

    _print_result(result)
    save_manifest(target, profile)
    console.print("[success]Manifest written.[/]")


@click.command()
@click.argument("target", type=click.Path(exists=True, file_okay=False, path_type=Path))
def update(target: Path) -> None:
    """Update an existing installation from its manifest."""
    target = target.resolve()
    config = load_config()
    manifest = load_manifest(target)

    if manifest is None:
        print_error("No .manifest.json found. Run 'cpc install' first.")
        raise SystemExit(1)

    if manifest.profile not in config.profiles:
        print_error(f"Profile '{manifest.profile}' no longer exists in config.")
        raise SystemExit(1)

    profile = config.profiles[manifest.profile]

    # Run source update commands
    for source in config.skill_sources:
        if source.update:
            console.print(f"Updating source: [path]{source.path}[/]")
            subprocess.run(source.update, shell=True, check=False)

    # Resolve skills
    skill_dirs: list[Path] = []
    for skill_name in profile.skills:
        resolved = resolve_skill(skill_name, config.skill_sources)
        if resolved:
            skill_dirs.append(resolved)
        else:
            console.print(f"[warning]Skill not found: {skill_name}[/]")

    result = install_profile(
        target=target,
        rule_sets=profile.rules,
        skill_dirs=skill_dirs,
    )

    _print_result(result)
    save_manifest(target, profile)
    console.print("[success]Updated. Manifest written.[/]")
```

**Step 2: Update `discover_rules` in `config.py` to accept `rules_dir` parameter**

The `discover_rules` function in `config.py` needs to accept an optional `rules_dir`
parameter so tests can pass a temp directory:

```python
def discover_rules(rule_sets: list[RuleSet], *, rules_dir: Path = RULES_DIR) -> dict[RuleSet, list[Path]]:
    """Find all .md files for the given rule sets."""
    result: dict[RuleSet, list[Path]] = {}
    for rule_set in rule_sets:
        set_dir = rules_dir / rule_set.value
        if set_dir.is_dir():
            result[rule_set] = sorted(set_dir.glob("*.md"))
        else:
            result[rule_set] = []
    return result
```

**Step 3: Run tests — verify they pass (TDD green phase)**

Run: `uv run pytest tests/test_linker.py -v`
Expected: All 9 tests PASS

**Step 4: Commit**

```bash
git add src/cpc/linker.py src/cpc/config.py
git commit -m "feat: implement linker with install/update commands — all tests pass"
```

---

### Task 6: Wire up CLI and register commands

**Files:**
- Modify: `src/cpc/cli.py`

**Step 1: Register all commands in `cli.py`**

```python
"""CLI entry point — assembles click group from submodules."""

import click

from cpc.config import status
from cpc.linker import install, update


@click.group()
def main() -> None:
    """Manage Claude Code rules and skills across projects."""


main.add_command(install)
main.add_command(update)
main.add_command(status)

if __name__ == "__main__":
    main()
```

**Step 2: Verify all commands appear in help**

Run: `uv run cpc --help`
Expected: Shows `install`, `update`, and `status` commands.

**Step 3: Verify subcommand help works**

Run: `uv run cpc install --help`
Expected: Shows `--profile` option and `TARGET` argument.

Run: `uv run cpc status --help`
Expected: Shows `TARGET` argument.

**Step 4: Commit**

```bash
git add src/cpc/cli.py
git commit -m "feat: wire up install, update, and status commands in CLI"
```

---

### Task 7: Create skills directory and verify end-to-end

**Files:**
- Create: `skills/.gitkeep`
- Delete: `install.py`

**Step 1: Create skills directory**

```bash
mkdir -p skills
touch skills/.gitkeep
```

**Step 2: Run full test suite**

Run: `uv run pytest tests/ -v`
Expected: All tests PASS

**Step 3: Verify end-to-end against real project (non-destructive check)**

Run: `uv run cpc install /Users/koi/Repositories/myersadamk/astro-template --profile astro`
Expected: Colored output showing updated symlinks for rules, linked/not-found for skills.

Run: `uv run cpc status /Users/koi/Repositories/myersadamk/astro-template`
Expected: Shows profile "astro", rule sets, skills, symlink health.

Run: `uv run cpc update /Users/koi/Repositories/myersadamk/astro-template`
Expected: Runs source update commands, re-applies symlinks, shows result.

**Step 4: Delete old `install.py`**

```bash
rm install.py
```

**Step 5: Commit**

```bash
git add skills/.gitkeep
git rm install.py
git commit -m "feat: add skills directory, remove old install.py"
```

---

### Task 8: Update README.md

**Files:**
- Modify: `README.md`

**Step 1: Update README to reflect new CLI**

Replace the Install section and add skills documentation. Key changes:
- `python3 install.py` → `uv run cpc install`
- Add profiles section
- Add skills section
- Add `config.yaml` documentation
- Update verification gate section (unchanged)

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: update README for new cpc CLI and skills support"
```

---

### Task 9: Final verification

**Step 1: Run full test suite**

Run: `uv run pytest tests/ -v`
Expected: All tests PASS

**Step 2: Verify both projects work**

Run: `uv run cpc install /Users/koi/Repositories/myersadamk/astro-template --profile astro`
Run: `uv run cpc install /Users/koi/Repositories/myersadamk/myersadamk-site --profile nextjs`
Run: `uv run cpc status /Users/koi/Repositories/myersadamk/astro-template`
Run: `uv run cpc status /Users/koi/Repositories/myersadamk/myersadamk-site`

Expected: Both projects show correct profiles, healthy symlinks.

**Step 3: Verify `--help` is clean**

Run: `uv run cpc --help`
Run: `uv run cpc install --help`
Run: `uv run cpc update --help`
Run: `uv run cpc status --help`

All should show clean help text.
