"""CLI entry point — assembles click group from submodules."""

import os
from pathlib import Path

import click

from cpc.config import REPO_ROOT, status
from cpc.console import console, print_error
from cpc.linker import install, update

WRAPPER_PATH = REPO_ROOT / "bin" / "cpc"
DEFAULT_BIN_DIR = Path("/usr/local/bin")


@click.group()
def main() -> None:
    """Manage Claude Code rules and skills across projects."""


@click.command()
@click.option(
    "--bin-dir",
    type=click.Path(file_okay=False, path_type=Path),
    default=DEFAULT_BIN_DIR,
    help="Directory to symlink into.",
)
def init(bin_dir: Path) -> None:
    """Set up cpc for global use by symlinking into PATH."""
    dest = bin_dir / "cpc"

    if dest.is_symlink():
        existing_target = dest.resolve()
        if existing_target == WRAPPER_PATH.resolve():
            console.print(f"[success]Already installed:[/] {dest} -> {WRAPPER_PATH}")
            return
        console.print(f"[warning]Existing symlink:[/] {dest} -> {existing_target}")
        if not click.confirm("Replace it?"):
            return
        dest.unlink()
    elif dest.exists():
        print_error(f"{dest} exists and is not a symlink. Remove it manually to proceed.")
        raise SystemExit(1)

    if not bin_dir.exists():
        print_error(f"Directory {bin_dir} does not exist.")
        raise SystemExit(1)

    rel_path = os.path.relpath(WRAPPER_PATH, bin_dir)
    try:
        dest.symlink_to(rel_path)
    except PermissionError:
        print_error(f"Permission denied writing to {bin_dir}.")
        console.print(f"  Run: [label]sudo cpc init[/]")
        console.print(f"  Or:  [label]cpc init --bin-dir ~/.local/bin[/]")
        raise SystemExit(1)
    console.print(f"[success]Linked:[/] {dest} -> {WRAPPER_PATH}")
    console.print("\nYou can now run [label]cpc[/] from anywhere.")


main.add_command(init)
main.add_command(install)
main.add_command(update)
main.add_command(status)

if __name__ == "__main__":
    main()
