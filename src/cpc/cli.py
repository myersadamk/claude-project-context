"""CLI entry point — assembles click group from submodules."""

import click


@click.group()
def main() -> None:
    """Manage Claude Code rules and skills across projects."""


if __name__ == "__main__":
    main()
