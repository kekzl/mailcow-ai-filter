"""FilterRule value object representing a complete filter rule."""

from dataclasses import dataclass
from typing import Self

from .filter_action import FilterAction
from .filter_condition import FilterCondition


@dataclass(frozen=True, slots=True)
class FilterRule:
    """Immutable filter rule combining conditions and actions.

    A rule consists of:
    - One or more conditions (matched with AND/OR logic)
    - One or more actions to perform if conditions match
    - Logical operator for combining conditions
    """

    conditions: tuple[FilterCondition, ...]
    actions: tuple[FilterAction, ...]
    logical_operator: str = "anyof"  # "anyof" (OR) or "allof" (AND)
    name: str = ""
    description: str = ""

    def __post_init__(self) -> None:
        """Validate rule on construction."""
        if not self.conditions:
            raise ValueError("Filter rule must have at least one condition")
        if not self.actions:
            raise ValueError("Filter rule must have at least one action")
        if self.logical_operator not in ("anyof", "allof"):
            raise ValueError(f"Invalid logical operator: {self.logical_operator}")

    @classmethod
    def create(
        cls,
        conditions: list[FilterCondition],
        actions: list[FilterAction],
        logical_operator: str = "anyof",
        name: str = "",
        description: str = "",
    ) -> Self:
        """Factory method to create a validated filter rule."""
        return cls(
            conditions=tuple(conditions),
            actions=tuple(actions),
            logical_operator=logical_operator,
            name=name,
            description=description,
        )

    def to_sieve(self) -> str:
        """Convert rule to Sieve script syntax."""
        lines = []

        # Add name and description as comments
        if self.name:
            lines.append(f"# Rule: {self.name}")
        if self.description:
            lines.append(f"# Description: {self.description}")

        # Build condition block
        if len(self.conditions) == 1:
            lines.append(f"if {self.conditions[0].to_sieve()} {{")
        else:
            lines.append(f"if {self.logical_operator} (")
            for i, condition in enumerate(self.conditions):
                comma = "," if i < len(self.conditions) - 1 else ""
                lines.append(f"  {condition.to_sieve()}{comma}")
            lines.append(") {")

        # Add actions
        for action in self.actions:
            lines.append(f"  {action.to_sieve()}")

        lines.append("}")

        return "\n".join(lines)

    def matches_all_conditions(self) -> bool:
        """Check if rule requires all conditions to match (AND logic)."""
        return self.logical_operator == "allof"

    def matches_any_condition(self) -> bool:
        """Check if rule requires any condition to match (OR logic)."""
        return self.logical_operator == "anyof"

    def __str__(self) -> str:
        cond_str = f" {self.logical_operator} ".join(str(c) for c in self.conditions)
        action_str = ", ".join(str(a) for a in self.actions)
        return f"IF {cond_str} THEN {action_str}"
