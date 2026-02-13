#!/usr/bin/env python3
"""Install shared Claude Code rules into a target project via symlinks."""

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

RULES_DIR = Path(__file__).resolve().parent / "rules"
MANIFEST_NAME = ".manifest.json"


def discover_sets() -> dict[str, list[Path]]:
    """Find all rule sets and their .md files."""
    sets: dict[str, list[Path]] = {}
    for entry in sorted(RULES_DIR.iterdir()):
        if entry.is_dir() and not entry.name.startswith("."):
            md_files = sorted(entry.glob("*.md"))
            if md_files:
                sets[entry.name] = md_files
    return sets


def interactive_select(available: dict[str, list[Path]]) -> list[str]:
    """Present numbered list of rule sets for selection."""
    print("\nAvailable rule sets:\n")
    names = list(available.keys())
    for i, name in enumerate(names, 1):
        files = [f.name for f in available[name]]
        print(f"  {i}. {name}")
        for f in files:
            print(f"       - {f}")
        print()

    print("Enter set numbers separated by spaces (e.g., 1 2 3)")
    print("Or 'all' to select everything.\n")

    while True:
        choice = input("> ").strip()
        if choice.lower() == "all":
            return names
        try:
            indices = [int(x) for x in choice.split()]
            selected = [names[i - 1] for i in indices if 1 <= i <= len(names)]
            if selected:
                return selected
            print("No valid selections. Try again.")
        except (ValueError, IndexError):
            print("Invalid input. Enter numbers separated by spaces.")


def load_manifest(target: Path) -> dict | None:
    """Load existing manifest from target project."""
    manifest_path = target / ".claude" / "rules" / MANIFEST_NAME
    if manifest_path.exists():
        with open(manifest_path) as f:
            return json.load(f)
    return None


def save_manifest(target: Path, source: Path, selected: list[str]) -> None:
    """Write manifest recording selections and source path."""
    manifest_path = target / ".claude" / "rules" / MANIFEST_NAME
    manifest = {
        "source": str(source),
        "sets": selected,
        "installed": str(date.today()),
    }
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")


def install_rules(
    target: Path,
    selected_sets: list[str],
    available: dict[str, list[Path]],
) -> None:
    """Symlink rule files into target project's .claude/rules/."""
    rules_dir = target / ".claude" / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)

    linked = []
    skipped = []
    updated = []
    cleaned = []

    # Determine which files SHOULD exist as symlinks from this source
    expected_symlinks: set[str] = set()
    for set_name in selected_sets:
        for src_file in available[set_name]:
            expected_symlinks.add(src_file.name)

    # Clean stale symlinks that point into our rules dir but are no longer
    # part of the selected sets
    for existing in rules_dir.iterdir():
        if existing.name == MANIFEST_NAME:
            continue
        if existing.is_symlink():
            link_target = existing.resolve()
            if str(RULES_DIR) in str(link_target) and existing.name not in expected_symlinks:
                existing.unlink()
                cleaned.append(existing.name)

    # Install symlinks
    for set_name in selected_sets:
        for src_file in available[set_name]:
            dest = rules_dir / src_file.name
            rel_source = os.path.relpath(src_file, rules_dir)

            if dest.exists() or dest.is_symlink():
                if dest.is_symlink():
                    # Replace existing symlink
                    dest.unlink()
                    dest.symlink_to(rel_source)
                    updated.append(src_file.name)
                else:
                    # Non-symlink file exists — local override, skip
                    skipped.append(src_file.name)
            else:
                dest.symlink_to(rel_source)
                linked.append(src_file.name)

    # Summary
    print(f"\n{'=' * 50}")
    print(f"Installed to: {rules_dir}")
    print(f"Sets: {', '.join(selected_sets)}")
    print(f"{'=' * 50}")

    if linked:
        print(f"\n  Linked ({len(linked)}):")
        for f in linked:
            print(f"    + {f}")

    if updated:
        print(f"\n  Updated ({len(updated)}):")
        for f in updated:
            print(f"    ~ {f}")

    if skipped:
        print(f"\n  Skipped — local override ({len(skipped)}):")
        for f in skipped:
            print(f"    ! {f}")

    if cleaned:
        print(f"\n  Cleaned — stale symlinks ({len(cleaned)}):")
        for f in cleaned:
            print(f"    - {f}")

    total = len(linked) + len(updated)
    print(f"\n  Total active symlinks: {total}")
    if skipped:
        print(f"  Local overrides preserved: {len(skipped)}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Install shared Claude Code rules into a project."
    )
    parser.add_argument(
        "target",
        type=Path,
        help="Path to the target project root",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Re-apply from existing .manifest.json (non-interactive)",
    )
    args = parser.parse_args()

    target = args.target.resolve()
    if not target.is_dir():
        print(f"Error: {target} is not a directory.", file=sys.stderr)
        sys.exit(1)

    available = discover_sets()
    if not available:
        print(f"Error: No rule sets found in {RULES_DIR}", file=sys.stderr)
        sys.exit(1)

    if args.update:
        manifest = load_manifest(target)
        if not manifest:
            print("Error: No .manifest.json found. Run without --update first.", file=sys.stderr)
            sys.exit(1)
        selected = manifest["sets"]
        # Validate sets still exist
        missing = [s for s in selected if s not in available]
        if missing:
            print(f"Warning: Sets no longer available: {', '.join(missing)}", file=sys.stderr)
            selected = [s for s in selected if s in available]
        print(f"Updating from manifest: {', '.join(selected)}")
    else:
        selected = interactive_select(available)

    install_rules(target, selected, available)
    save_manifest(target, RULES_DIR.parent, selected)
    print("Done. Manifest written to .claude/rules/.manifest.json")


if __name__ == "__main__":
    main()
