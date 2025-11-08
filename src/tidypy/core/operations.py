"""Planning and execution utilities for filesystem operations.

The planning stage generates rename operations based on rules, while the
execution stage applies them to the filesystem with optional dry-run mode.
"""

from __future__ import annotations

from pathlib import Path
import shutil
from typing import Iterable

from .models import PlannedOperation
from .scanner import scan_directory
from .rules import RULES

__all__ = ["plan_operations", "apply_operations"]


def _resolve_root(path: str | Path) -> Path:
    """Return an absolute directory path or raise ValueError when invalid."""

    root = Path(path).expanduser().resolve()
    if not root.exists():
        raise ValueError(f"Path does not exist: {root}")
    if not root.is_dir():
        raise ValueError(f"Path is not a directory: {root}")
    return root


def plan_operations(
    path: str | Path,
    recursive: bool = False,
    rule_name: str = "dots_to_spaces",
) -> list[PlannedOperation]:
    """Plan rename operations for all items in a directory."""

    root = _resolve_root(path)
    items = scan_directory(root, recursive=recursive, include_root=False)

    rule = RULES.get(rule_name)
    if rule is None:
        raise ValueError(f"Unknown rule: {rule_name}")

    planned_operations: list[PlannedOperation] = []
    for item in items:
        new_path = rule(item.path)

        # Skip items that would not change their name.
        if new_path.name == item.path.name:
            continue

        planned_operations.append(
            PlannedOperation(
                source=item.path,
                target=new_path,
                op_type="rename",
            )
        )

    return planned_operations


def _remove_existing_target(target: Path) -> None:
    """Remove an existing target path to allow overwriting."""

    if target.is_dir():
        shutil.rmtree(target)
    else:
        target.unlink()


def apply_operations(
    operations: Iterable[PlannedOperation],
    dry_run: bool = True,
    overwrite: bool = False,
) -> list[str]:
    """Apply planned rename operations and return human-readable log lines."""

    messages: list[str] = []

    for operation in operations:
        if operation.op_type != "rename":
            messages.append(
                f"SKIP: unsupported operation type '{operation.op_type}' for {operation.source}"
            )
            continue

        source = operation.source
        target = operation.target

        if source == target:
            messages.append(f"SKIP: source and target are identical: {source}")
            continue

        if not source.exists():
            messages.append(f"SKIP: source does not exist: {source}")
            continue

        if target.exists():
            if not overwrite:
                messages.append(
                    f"SKIP: target already exists and overwrite=False: {target}"
                )
                continue
            _remove_existing_target(target)

        if dry_run:
            messages.append(f"DRY-RUN: rename {source} -> {target}")
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            source.rename(target)
            messages.append(f"OK: rename {source} -> {target}")
        except OSError as error:
            messages.append(f"ERROR: failed to rename {source} -> {target}: {error}")

    return messages
