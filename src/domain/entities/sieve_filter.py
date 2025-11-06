"""SieveFilter entity - Aggregate root for Sieve filter rules."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Self

from ..value_objects.filter_rule import FilterRule


@dataclass
class SieveFilter:
    """SieveFilter aggregate root representing a complete Sieve filter script.

    This is the main entity for filter management with identity (id).
    Contains filter rules and generates Sieve script syntax.
    """

    id: str
    name: str
    description: str
    rules: list[FilterRule]
    enabled: bool = True
    priority: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    _domain_events: list = field(default_factory=list, init=False, repr=False)

    @classmethod
    def create(
        cls,
        name: str,
        description: str,
        rules: list[FilterRule] | None = None,
        enabled: bool = True,
        priority: int = 0,
    ) -> Self:
        """Factory method to create SieveFilter with validation.

        Args:
            name: Filter name
            description: Filter description
            rules: List of filter rules
            enabled: Whether filter is enabled
            priority: Filter priority (higher = processed first)

        Returns:
            New SieveFilter entity

        Raises:
            ValueError: If validation fails
        """
        if not name:
            raise ValueError("Filter name cannot be empty")

        return cls(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            rules=rules or [],
            enabled=enabled,
            priority=priority,
        )

    def add_rule(self, rule: FilterRule) -> None:
        """Add a rule to the filter.

        Domain operation to add rules with validation.

        Args:
            rule: FilterRule to add
        """
        self.rules.append(rule)
        self.updated_at = datetime.now()

    def remove_rule(self, rule: FilterRule) -> None:
        """Remove a rule from the filter.

        Args:
            rule: FilterRule to remove
        """
        self.rules.remove(rule)
        self.updated_at = datetime.now()

    def enable(self) -> None:
        """Enable the filter."""
        self.enabled = True
        self.updated_at = datetime.now()

    def disable(self) -> None:
        """Disable the filter."""
        self.enabled = False
        self.updated_at = datetime.now()

    def to_sieve_script(self) -> str:
        """Convert filter to complete Sieve script.

        Domain logic to generate valid Sieve syntax.

        Returns:
            Complete Sieve script as string
        """
        lines = []

        # Header
        lines.append("# Sieve Filter Rules")
        lines.append(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"# Filter: {self.name}")
        if self.description:
            lines.append(f"# Description: {self.description}")
        lines.append("#")
        lines.append("# IMPORTANT: Review these rules before activating!")
        lines.append("")
        lines.append('require ["fileinto", "envelope", "imap4flags"];')
        lines.append("")

        # Rules
        for rule in self.rules:
            lines.append(rule.to_sieve())
            lines.append("")

        # Footer
        lines.append("# End of AI-generated rules")
        lines.append("# All other mail goes to Inbox (default)")

        return "\n".join(lines)

    def validate(self) -> tuple[bool, list[str]]:
        """Validate filter configuration.

        Domain validation logic.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        if not self.name:
            errors.append("Filter must have a name")

        if not self.rules:
            errors.append("Filter must have at least one rule")

        for i, rule in enumerate(self.rules):
            if not rule.conditions:
                errors.append(f"Rule {i+1} has no conditions")
            if not rule.actions:
                errors.append(f"Rule {i+1} has no actions")

        return len(errors) == 0, errors

    def get_domain_events(self) -> list:
        """Get and clear domain events."""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events

    def __eq__(self, other: object) -> bool:
        """Compare filters by ID."""
        if not isinstance(other, SieveFilter):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)

    def __str__(self) -> str:
        return f"SieveFilter(name='{self.name}', rules={len(self.rules)})"

    def __repr__(self) -> str:
        return f"SieveFilter(id='{self.id}', name='{self.name}', rules={len(self.rules)}, enabled={self.enabled})"
