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

    # 1. Create .claude/rules/ in target if needed
    claude_rules = target / ".claude" / "rules"
    claude_rules.mkdir(parents=True, exist_ok=True)

    # 2. Discover rule .md files for the given rule sets
    discovered = discover_rules(rule_sets, rules_dir=rules_dir)

    # Build set of expected rule filenames
    expected_files: set[str] = set()
    all_rule_files: list[Path] = []
    for rule_set, files in discovered.items():
        for f in files:
            expected_files.add(f.name)
            all_rule_files.append(f)

    # 3. Clean stale rule symlinks
    resolved_rules_dir = rules_dir.resolve()
    for entry in sorted(claude_rules.iterdir()):
        # SAFETY: is_symlink() check MUST come first
        if not entry.is_symlink():
            continue

        # Resolve the symlink target to check if it belongs to us
        resolved_target = entry.resolve()
        try:
            resolved_target.relative_to(resolved_rules_dir)
            is_ours = True
        except ValueError:
            is_ours = False

        if is_ours and entry.name not in expected_files:
            # Stale symlink that points into our rules_dir but is no longer needed
            entry.unlink()
            results.append(LinkResult(
                filename=entry.name,
                action=LinkAction.CLEANED,
            ))
        # If not ours: leave it alone (foreign symlink)

    # 4. Install rule symlinks
    for rule_file in all_rule_files:
        dest = claude_rules / rule_file.name

        # SAFETY: is_symlink() MUST be checked before exists()
        if dest.is_symlink():
            # Replace existing symlink (UPDATED)
            dest.unlink()
            rel_path = os.path.relpath(rule_file, dest.parent)
            dest.symlink_to(rel_path)
            results.append(LinkResult(
                filename=rule_file.name,
                action=LinkAction.UPDATED,
                target=rule_file,
            ))
        elif dest.exists():
            # Non-symlink file exists — skip (local override, NEVER overwrite)
            results.append(LinkResult(
                filename=rule_file.name,
                action=LinkAction.SKIPPED,
                target=rule_file,
            ))
        else:
            # Create new symlink (LINKED)
            rel_path = os.path.relpath(rule_file, dest.parent)
            dest.symlink_to(rel_path)
            results.append(LinkResult(
                filename=rule_file.name,
                action=LinkAction.LINKED,
                target=rule_file,
            ))

    # 5. If skill_dirs is non-empty, create .claude/skills/ and symlink each
    if skill_dirs:
        claude_skills = target / ".claude" / "skills"
        claude_skills.mkdir(parents=True, exist_ok=True)

        # 5a. Clean stale skill symlinks
        expected_skill_names = {sd.name for sd in skill_dirs}
        skill_source_parents = {sd.parent.resolve() for sd in skill_dirs}

        for existing in claude_skills.iterdir():
            if not existing.is_symlink():
                continue
            if existing.name in expected_skill_names:
                continue
            # Check if this symlink points into one of our skill sources
            try:
                resolved = existing.resolve()
                for parent in skill_source_parents:
                    resolved.relative_to(parent)
                    # It's ours and stale — clean it
                    existing.unlink()
                    results.append(LinkResult(existing.name, LinkAction.CLEANED))
                    break
            except ValueError:
                continue  # Foreign symlink, leave it alone

        for skill_dir in skill_dirs:
            dest = claude_skills / skill_dir.name

            # SAFETY: is_symlink() MUST be checked before exists()
            if dest.is_symlink():
                dest.unlink()
                rel_path = os.path.relpath(skill_dir, dest.parent)
                dest.symlink_to(rel_path)
                results.append(LinkResult(
                    filename=skill_dir.name,
                    action=LinkAction.UPDATED,
                    target=skill_dir,
                ))
            elif dest.exists():
                # Non-symlink — skip
                results.append(LinkResult(
                    filename=skill_dir.name,
                    action=LinkAction.SKIPPED,
                    target=skill_dir,
                ))
            else:
                rel_path = os.path.relpath(skill_dir, dest.parent)
                dest.symlink_to(rel_path)
                results.append(LinkResult(
                    filename=skill_dir.name,
                    action=LinkAction.LINKED,
                    target=skill_dir,
                ))

    # 6. Build profile name from rule sets for InstallResult
    profile_name = "+".join(rs.value for rs in rule_sets) if rule_sets else "custom"

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
        rules_str = ", ".join(r.value for r in profile.rules)
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


# -- Click commands ----------------------------------------------------------


@click.command()
@click.argument("target", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--profile", "profile_name", default=None, help="Profile name (non-interactive).")
def install(target: Path, profile_name: str | None) -> None:
    """Install rules and skills into a project."""
    target = target.resolve()
    config = load_config()

    if profile_name is not None:
        if profile_name not in config.profiles:
            print_error(f"Profile '{profile_name}' not found in config.")
            raise SystemExit(1)
        profile = config.profiles[profile_name]
    else:
        profile = _select_profile(config)

    # Resolve skill directories
    skill_dirs: list[Path] = []
    for skill_name in profile.skills:
        skill_path = resolve_skill(skill_name, config.skill_sources)
        if skill_path is None:
            print_error(f"Skill '{skill_name}' not found in any source.")
            raise SystemExit(1)
        skill_dirs.append(skill_path)

    result = install_profile(
        target=target,
        rule_sets=profile.rules,
        skill_dirs=skill_dirs,
    )

    _print_result(result)
    save_manifest(target, profile)


@click.command()
@click.argument("target", type=click.Path(exists=True, file_okay=False, path_type=Path))
def update(target: Path) -> None:
    """Update an existing installation from its manifest."""
    target = target.resolve()
    manifest = load_manifest(target)

    if manifest is None:
        print_error(f"No installation found in {target}. Run 'install' first.")
        raise SystemExit(1)

    config = load_config()

    if manifest.profile not in config.profiles:
        print_error(f"Profile '{manifest.profile}' no longer exists in config.")
        raise SystemExit(1)

    profile = config.profiles[manifest.profile]

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

    # Resolve skill directories
    skill_dirs: list[Path] = []
    for skill_name in profile.skills:
        skill_path = resolve_skill(skill_name, config.skill_sources)
        if skill_path is not None:
            skill_dirs.append(skill_path)

    result = install_profile(
        target=target,
        rule_sets=profile.rules,
        skill_dirs=skill_dirs,
    )

    _print_result(result)
    save_manifest(target, profile)
