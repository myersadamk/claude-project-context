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
