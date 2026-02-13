"""Config loading, types, and the `status` command."""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

import click
import yaml

from cpc.console import console, print_error

MANIFEST_NAME = ".cpc.manifest.json"


def _find_repo_root() -> Path:
    """Walk up from this file to find the repo root (contains pyproject.toml)."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError("Could not find repo root (no pyproject.toml found)")


REPO_ROOT = _find_repo_root()
RULES_DIR = REPO_ROOT / "rules"


# ── Types ──────────────────────────────────────────────────────────


class RuleSet(StrEnum):
    """Available rule set names, matching rules/ subdirectories."""

    UNIVERSAL = "universal"
    TYPESCRIPT_WEB = "typescript-web"
    ASTRO = "astro"
    NEXTJS = "nextjs"
    PYTHON = "python"
    PYTHON_CLI = "python-cli"


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
    """Recorded state of an installation, written to .cpc.manifest.json."""

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
    """Load .cpc.manifest.json from a target project."""
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
    """Write .cpc.manifest.json to the target project."""
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


# ── Status command ─────────────────────────────────────────────────


@click.command()
@click.argument("target", type=click.Path(exists=True, file_okay=False, path_type=Path))
def status(target: Path) -> None:
    """Show installed profile, rule sets, skills, and symlink health."""
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
            console.print(f"  [error]\u2717[/] {b}")
    else:
        console.print("\n[success]All symlinks healthy.[/]")
    console.print()
