"""Command-line interface for the TidyPy application.

This module exposes a Typer-based CLI that forwards work to the core logic.
Current commands:
- scan     → list directory contents using the core scanner
- preview  → show placeholder planned operations
- version  → display CLI version
"""

from __future__ import annotations

from pathlib import Path

import typer

from tidypy.core.operations import plan_operations
from tidypy.core.scanner import scan_directory

app = typer.Typer(
    help="TidyPy command-line interface",
    no_args_is_help=True,
)

@app.callback()
def root() -> None:
    """Root command group for TidyPy CLI."""
    # Callback forces multi-command mode; no extra work at the moment.
    return None


def _format_size(size: int | None) -> str:
    """Return a human-readable file size string."""
    if size is None:
        return ""
    value = float(size)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if value < 1024:
            return f"({value:.0f} {unit})"
        value /= 1024
    return f"({value:.1f} PB)"


def _format_operation_label(operation) -> str:
    """Return a human-readable label for a planned operation."""
    return f"[{operation.op_type.upper()}] {operation.source} -> {operation.target}"


def _validate_directory(value: str) -> Path:
    """Convert string input to an absolute directory path or raise an error."""
    path = Path(value).expanduser().resolve()
    if not path.exists():
        raise typer.BadParameter(f"Path does not exist: {path}")
    if not path.is_dir():
        raise typer.BadParameter(f"Path is not a directory: {path}")
    return path


@app.command("scan")
def scan(
    path: Path = typer.Argument(
        ...,
        callback=_validate_directory,
        help="Directory to scan",
    ),
    recursive: bool = typer.Option(
        False,
        "--recursive",
        "-r",
        help="Traverse directories recursively",
    ),
    include_root: bool = typer.Option(
        True,
        "--include-root/--no-include-root",
        help="Include the root directory in the output",
    ),
) -> None:
    """List items within a directory using the core scanner."""
    try:
        items = scan_directory(path=path, recursive=recursive, include_root=include_root)
    except ValueError as error:
        typer.echo(f"Error: {error}")
        raise typer.Exit(code=1) from error

    root_path = path.resolve()

    for item in items:
        if not include_root and item.path == root_path:
            continue

        label = "[DIR]" if item.is_dir else "[FILE]"
        size_text = "" if item.is_dir else _format_size(item.size)
        typer.echo(f"{label:<7} {item.path} {size_text}")


@app.command("preview")
def preview(
    path: Path = typer.Argument(
        ...,
        callback=_validate_directory,
        help="Directory to preview",
    ),
    recursive: bool = typer.Option(
        False,
        "--recursive",
        "-r",
        help="Traverse directories recursively",
    ),
    rule: str = typer.Option(
        "dots_to_spaces",
        "--rule",
        "-R",
        help="Rename rule to apply",
    ),
) -> None:
    """Preview planned operations without touching the filesystem."""
    try:
        operations = plan_operations(path=path, recursive=recursive)
    except ValueError as error:
        typer.echo(f"Error: {error}")
        raise typer.Exit(code=1) from error

    if not operations:
        typer.echo("No planned operations found.")
        return

    for operation in operations:
        # Skip operations where source == target (no actual change)
        if operation.source == operation.target:
            continue
        typer.echo(_format_operation_label(operation))

@app.command("version", help="Show TidyPy CLI version.")
def version() -> None:
    """Display current CLI version."""
    typer.echo("TidyPy CLI version 0.1.0")


def main() -> None:
    """Entrypoint used by `python -m src.tidypy.ui.cli_app`."""
    app()


if __name__ == "__main__":
    main()