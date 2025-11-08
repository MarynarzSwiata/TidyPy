"""Planning utilities for filesystem operations.

For now the planning layer produces placeholder rename operations for every
item discovered by the scanner. The goal is to provide a structure that can be
extended with real renaming/move/copy rules in subsequent iterations.
#TODO
- teraz target=item.path → czyli “rename z nazwą taką samą jak źródło”. To OK na MVP, ale jak tylko dodamy reguły, to będziemy tu wstrzykiwać funkcję rule.
- dodałbym jeszcze __all__ = ["plan_operations"] – już jest, więc jest porządek eksportów
"""

from __future__ import annotations
from pathlib import Path
from .models import PlannedOperation
from .scanner import scan_directory
from .rules import RULES

__all__ = ["plan_operations"]


def plan_operations(
    path: str | Path,
    recursive: bool = False,
    rule_name: str = "dots_to_spaces",
) -> list[PlannedOperation]:
    """Plan rename operations for all items in a directory."""
    root = Path(path).expanduser().resolve()

    if not root.exists():
        raise ValueError(f"Path does not exist: {root}")
    if not root.is_dir():
        raise ValueError(f"Path is not a directory: {root}")

    items = scan_directory(root, recursive=recursive, include_root=False)

    rule = RULES.get(rule_name)
    if rule is None:
        raise ValueError(f"Unknown rule: {rule_name}")

    planned_operations: list[PlannedOperation] = []
    for item in items:
        new_path = rule(item.path)

        # skip items that don't actually change
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
