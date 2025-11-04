"""Core data models for TidyPy.

This module defines small, focused dataclasses that represent the
domain objects shared between the core logic, CLI, and GUI layers.

All names and comments are in English as required.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

# Public re-exports of types from this module
__all__ = [
    "OperationType",
    "FileItem",
    "PlannedOperation",
]


# A narrow string type describing the kind of operation to perform.
# Using Literal keeps the values simple strings while still providing
# type-checker support across the codebase.
OperationType = Literal["rename", "move", "copy"]


@dataclass(slots=True)
class FileItem:
    """Represents a file system entry discovered during scanning.

    Attributes:
        path: Absolute path to the entry. All paths in the project
              are normalized to absolute form to avoid ambiguity
              during preview/apply phases and in logs.
        is_dir: True if entry is a directory, False if it is a file.
        size: Size in bytes for files when known; None for directories
              or when size computation is skipped.
    """

    path: Path
    is_dir: bool
    size: int | None = None


@dataclass(slots=True)
class PlannedOperation:
    """A planned change to the file system.

    The core logic produces a list of planned operations which can be
    previewed (dry run) or applied. Both CLI and GUI should consume
    this model without modification.

    Attributes:
        source: Original path of the file or directory.
        target: Destination path after the operation.
        op_type: Kind of operation, one of: "rename", "move", "copy".
    """

    source: Path
    target: Path
    op_type: OperationType

    def is_rename(self) -> bool:
        """Return True when this operation is a rename within the same directory."""
        return self.op_type == "rename"

    def is_move(self) -> bool:
        """Return True when this operation moves an entry to another location."""
        return self.op_type == "move"

    def is_copy(self) -> bool:
        """Return True when this operation copies an entry to another location."""
        return self.op_type == "copy"
