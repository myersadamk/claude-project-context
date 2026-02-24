"""Safety-critical symlink manager for installing rules and skills.

This module manages symlinks in a target project's .claude/ directory.
It follows strict safety invariants:
  - NEVER delete or overwrite a non-symlink file (local overrides are sacred)
  - NEVER remove symlinks that don't point into our rules_dir (foreign symlinks)
  - NEVER create files outside .claude/ in the target
  - is_symlink() check MUST come before exists() when deciding skip vs replace
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

import click

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
from cpc.console import (
    console,
    print_cleaned,
    print_error,
    print_heading,
    print_linked,
    print_rule,
    print_skipped,
    print_updated,
    print_warning,
)


# -- Result types -----------------------------------------------------------


class LinkAction(StrEnum):
    LINKED = "linked"
    UPDATED = "updated"
    SKIPPED = "skipped"
    CLEANED = "cleaned"


@dataclass(frozen=True)
class LinkResult:
    filename: str
    action: LinkAction
    target: Path | None = None


@dataclass(frozen=True)
class InstallResult:
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


# -- Symlink helpers ---------------------------------------------------------


def _is_owned_by(symlink: Path, owned_parents: set[Path]) -> bool:
    """Check if a symlink's target lives under one of our owned directories."""
    resolved = symlink.resolve()
    for parent in owned_parents:
        try:
            resolved.relative_to(parent)
            return True
        except ValueError:
            continue
    return False


def _clean_stale_symlinks(
    *,
    directory: Path,
    expected_names: set[str],
    owned_parents: set[Path],
    results: list[LinkResult],
) -> None:
    """Remove symlinks we own that are no longer in the expected set.

    SAFETY: Only removes symlinks whose targets resolve under owned_parents.
    Non-symlinks and foreign symlinks are never touched.
    """
    for entry in sorted(directory.iterdir()):
        if not entry.is_symlink():
            continue
        if entry.name in expected_names:
            continue
        if _is_owned_by(entry, owned_parents):
            entry.unlink()
            results.append(LinkResult(entry.name, LinkAction.CLEANED))


def _link_items(
    *,
    sources: list[Path],
    dest_dir: Path,
    results: list[LinkResult],
) -> None:
    """Create or update symlinks for each source into dest_dir.

    SAFETY: is_symlink() is checked before exists() — a non-symlink file
    is never overwritten (local overrides are sacred).
    """
    for source in sources:
        dest = dest_dir / source.name

        if dest.is_symlink():
            dest.unlink()
            rel_path = os.path.relpath(source, dest.parent)
            dest.symlink_to(rel_path)
            results.append(LinkResult(source.name, LinkAction.UPDATED, source))
        elif dest.exists():
            results.append(LinkResult(source.name, LinkAction.SKIPPED, source))
        else:
            rel_path = os.path.relpath(source, dest.parent)
            dest.symlink_to(rel_path)
            results.append(LinkResult(source.name, LinkAction.LINKED, source))


def _sync_directory(
    *,
    dest_dir: Path,
    sources: list[Path],
    owned_parents: set[Path],
    results: list[LinkResult],
) -> None:
    """Clean stale symlinks then install/update symlinks in a single directory."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    expected_names = {s.name for s in sources}
    _clean_stale_symlinks(
        directory=dest_dir,
        expected_names=expected_names,
        owned_parents=owned_parents,
        results=results,
    )
    _link_items(sources=sources, dest_dir=dest_dir, results=results)


# -- Core function -----------------------------------------------------------


def install_profile(
    *,
    target: Path,
    rule_sets: list[RuleSet],
    skill_dirs: list[Path],
    rules_dir: Path = RULES_DIR,
) -> InstallResult:
    """Install rules and skills into a target project's .claude/ directory.

    This is the safety-critical function. It creates symlinks for rule files
    and skill directories, cleans stale symlinks, and never touches non-symlink
    files or foreign symlinks.
    """
    results: list[LinkResult] = []

    discovered = discover_rules(rule_sets, rules_dir=rules_dir)
    all_rule_files = [f for files in discovered.values() for f in files]

    _sync_directory(
        dest_dir=target / ".claude" / "rules",
        sources=all_rule_files,
        owned_parents={rules_dir.resolve()},
        results=results,
    )

    if skill_dirs:
        _sync_directory(
            dest_dir=target / ".claude" / "skills",
            sources=skill_dirs,
            owned_parents={sd.parent.resolve() for sd in skill_dirs},
            results=results,
        )

    profile_name = "+".join(rule_sets) if rule_sets else "custom"
    return InstallResult(
        target_dir=target,
        profile=profile_name,
        results=results,
    )


# -- Interactive profile selection -------------------------------------------


def _select_profile(config: Config) -> Profile:
    """Print numbered list of profiles and prompt user to select one."""
    profiles = list(config.profiles.values())
    if not profiles:
        print_error("No profiles defined in config.")
        raise SystemExit(1)

    print_heading("Available profiles:")
    for i, profile in enumerate(profiles, 1):
        rules_str = ", ".join(profile.rules)
        skills_str = ", ".join(profile.skills) if profile.skills else "(none)"
        console.print(f"  {i}. [label]{profile.name}[/]")
        console.print(f"     Rules:  {rules_str}")
        console.print(f"     Skills: {skills_str}")

    choice = click.prompt("\nSelect a profile", type=int)
    if choice < 1 or choice > len(profiles):
        print_error(f"Invalid choice: {choice}")
        raise SystemExit(1)

    return profiles[choice - 1]


# -- Print helper ------------------------------------------------------------


def _print_result(result: InstallResult) -> None:
    """Display install results using console helpers."""
    print_heading("Install results:")

    for lr in result.linked:
        print_linked(lr.filename)
    for lr in result.updated:
        print_updated(lr.filename)
    for lr in result.skipped:
        print_skipped(lr.filename)
    for lr in result.cleaned:
        print_cleaned(lr.filename)

    # Summary
    parts = []
    if result.linked:
        parts.append(f"{len(result.linked)} linked")
    if result.updated:
        parts.append(f"{len(result.updated)} updated")
    if result.skipped:
        parts.append(f"{len(result.skipped)} skipped")
    if result.cleaned:
        parts.append(f"{len(result.cleaned)} cleaned")

    console.print(f"\n  {', '.join(parts)}")
    print_rule()


# -- Gitignore management ----------------------------------------------------

_CPC_START = "# cpc:start (managed by cpc — do not edit)"
_CPC_END = "# cpc:end"


def _build_gitignore_section(
    *,
    rule_files: list[str],
    skill_names: list[str],
) -> str:
    """Build the cpc-managed .gitignore section."""
    lines = [_CPC_START]
    for rule in sorted(rule_files):
        lines.append(f".claude/rules/{rule}")
    for skill in sorted(skill_names):
        lines.append(f".claude/skills/{skill}")
    lines.append(".claude/.cpc.manifest.json")
    lines.append(_CPC_END)
    return "\n".join(lines) + "\n"


def update_gitignore(
    *,
    target: Path,
    rule_files: list[str],
    skill_names: list[str],
) -> None:
    """Create or update the cpc-managed section in .gitignore."""
    gitignore_path = target / ".gitignore"
    section = _build_gitignore_section(rule_files=rule_files, skill_names=skill_names)

    if not gitignore_path.exists():
        gitignore_path.write_text(section)
        return

    content = gitignore_path.read_text()

    if _CPC_START in content and _CPC_END in content:
        start_idx = content.index(_CPC_START)
        end_idx = content.index(_CPC_END) + len(_CPC_END)
        # Consume trailing newline if present
        if end_idx < len(content) and content[end_idx] == "\n":
            end_idx += 1
        content = content[:start_idx] + section + content[end_idx:]
    else:
        if not content.endswith("\n"):
            content += "\n"
        content += "\n" + section

    gitignore_path.write_text(content)


# -- Click commands ----------------------------------------------------------


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
