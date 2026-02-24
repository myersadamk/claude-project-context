"""Config loading, types, and the `status` command."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import NewType

import click
import yaml

from cpc.console import console, print_error, print_warning

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

RuleSet = NewType("RuleSet", str)
"""A validated rule set name corresponding to a rules/ subdirectory."""


def available_rule_sets(*, rules_dir: Path = RULES_DIR) -> list[RuleSet]:
    """Discover available rule sets from the rules/ directory."""
    if not rules_dir.is_dir():
        return []
    return sorted(RuleSet(d.name) for d in rules_dir.iterdir() if d.is_dir())


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
    profiles: list[str]
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

    known_sets = set(available_rule_sets())
    profiles: dict[str, Profile] = {}
    for name, data in raw.get("profiles", {}).items():
        rules: list[RuleSet] = []
        for r in data.get("rules", []):
            if r not in known_sets:
                print_warning(f"Profile '{name}' references unknown rule set '{r}'.")
            rules.append(RuleSet(r))
        skills = data.get("skills", [])
        profiles[name] = Profile(name=name, rules=rules, skills=skills)

    return Config(skill_sources=skill_sources, profiles=profiles)


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
        set_dir = rules_dir / rule_set
        if set_dir.is_dir():
            result[rule_set] = sorted(set_dir.glob("*.md"))
        else:
            result[rule_set] = []
    return result


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


# ── Status command ─────────────────────────────────────────────────


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
            console.print(f"  [error]\u2717[/] {b}")
    else:
        console.print("\n[success]All symlinks healthy.[/]")
    console.print()
