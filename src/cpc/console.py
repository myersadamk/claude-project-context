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


def print_warning(message: str) -> None:
    console.print(f"  [warning]![/] {message}")


def print_error(message: str) -> None:
    console.print(f"[error]Error:[/] {message}", style="error")


def print_heading(text: str) -> None:
    console.print(f"\n[label]{text}[/]")


def print_rule() -> None:
    console.rule()
