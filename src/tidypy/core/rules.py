"""
Rename rules for TidyPy.

This module contains small, composable functions that transform a Path
into another Path (same directory, different name).
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Callable


def dots_to_spaces(path: Path) -> Path:
    """Replace dots in the name with spaces. Keep file extension intact for files."""
    # if it's a directory on disk, we can safely replace the whole name
    if path.is_dir():
        new_name = path.name.replace(".", " ")
        return path.with_name(new_name)

    # for files: replace only in the stem, keep extension
    stem = path.stem.replace(".", " ")
    suffix = path.suffix
    new_name = f"{stem}{suffix}"
    return path.with_name(new_name)


RULES: Dict[str, Callable[[Path], Path]] = {
    "dots_to_spaces": dots_to_spaces,
}
