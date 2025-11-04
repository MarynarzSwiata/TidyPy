"""
TidyPy CLI Application
----------------------
Multi-command interface using Typer.

Commands:
- scan: Lists directory contents (recursively if specified)
- version: Shows current CLI version

Run examples:
    python -m src.tidypy.ui.cli_app scan . --recursive
    python -m src.tidypy.ui.cli_app version
"""

from __future__ import annotations

from pathlib import Path

import typer

from tidypy.core.scanner import scan_directory

app = typer.Typer(
    help="TidyPy command-line interface",
    no_args_is_help=True,
)


@app.callback()
def root() -> None:
    """Root command group for TidyPy CLI."""
    # nothing to do here yet; callback forces multi-command mode
    return None

"""Convert byte size to human-readable format (e.g., 2048 -> '2 KB')."""
def _format_size(size: int | None) -> str:
    """Return human-readable file size."""
    if size is None:
        return ""
    value: float = float(size)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if value < 1024:
            return f"({value:.0f} {unit})"
        value /= 1024
    return f"({value:.1f} PB)"


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
        # if user disabled root entry, skip it
        if not include_root and item.path == root_path:
            continue

        label = "[DIR]" if item.is_dir else "[FILE]"
        size_text = "" if item.is_dir else _format_size(item.size)
        typer.echo(f"{label:<7} {item.path} {size_text}")

"""Display current version of the TidyPy CLI tool."""
@app.command("version", help="Show TidyPy CLI version.")
def version() -> None:
    """Show current TidyPy CLI version."""
    typer.echo("TidyPy CLI version 0.1.0")


def main() -> None:
    """Entrypoint used by `python -m src.tidypy.ui.cli_app`."""
    app()


if __name__ == "__main__":
    main()
