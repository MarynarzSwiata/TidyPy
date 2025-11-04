"""Directory scanning utilities for TidyPy.

This module exposes a single function, `scan_directory`, which inspects a
given directory and returns a list of FileItem instances representing its
contents. The function supports both non-recursive and recursive traversal
using pathlib only, and performs basic validation of the input path.

Notes:
- The root path is expanded (`~`) and resolved to an absolute path.
- When `include_root=True`, the returned list starts with an entry for the
  root directory itself.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .models import FileItem

__all__ = ["scan_directory"]


def _iter_entries(root: Path, recursive: bool) -> Iterable[Path]:
    """Yield directory entries under `root`.

    - When `recursive` is False, only direct children are yielded.
    - When `recursive` is True, all descendants are yielded using rglob("*").
    """

    if recursive:
        # Use rglob("*") to traverse all descendants without including the root itself
        yield from root.rglob("*")
    else:
        # Only direct children; Path.iterdir() does not include the root itself
        yield from root.iterdir()


def scan_directory(
    path: str | Path,
    recursive: bool = False,
    include_root: bool = False,
) -> list[FileItem]:
    """Scan a directory and return discovered entries as FileItem objects.

    Args:
        path: The directory path to scan (string or Path). The path is
              expanded and resolved to an absolute path.
        recursive: When True, traverse subdirectories recursively.
        include_root: When True, include a FileItem for the root directory
                       as the first element of the result list.

    Returns:
        A list of FileItem objects representing files and directories found.

    Raises:
        ValueError: When the path does not exist or is not a directory.
    """

    # Normalize to absolute path and expand user home (~)
    root = Path(path).expanduser().resolve()

    if not root.exists():
        raise ValueError(f"Path does not exist: {root}")
    if not root.is_dir():
        raise ValueError(f"Path is not a directory: {root}")

    items: list[FileItem] = []

    # Optionally include the root directory itself
    if include_root:
        items.append(FileItem(path=root, is_dir=True, size=None))
    for entry in _iter_entries(root, recursive=recursive):
        is_dir = entry.is_dir()
        size: int | None
        if is_dir:
            size = None
        else:
            # For files, retrieve byte size via stat(); be defensive
            # against potential OS errors (permissions, transient issues).
            try:
                size = entry.stat().st_size
            except OSError:
                size = None

        items.append(FileItem(path=entry.resolve(), is_dir=is_dir, size=size))
    # Provide stable ordering for UI/CLI displays
    items.sort(key=lambda i: i.path.as_posix())
    return items
