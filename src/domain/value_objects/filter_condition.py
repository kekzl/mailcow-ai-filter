"""FilterCondition value object for Sieve filter conditions."""

from dataclasses import dataclass
from enum import Enum
from typing import Self


class ConditionType(Enum):
    """Types of filter conditions matching Sieve capabilities."""
    HEADER_CONTAINS = "header_contains"
    HEADER_IS = "header_is"
    ADDRESS_DOMAIN = "address_domain"
    ADDRESS_IS = "address_is"
    BODY_CONTAINS = "body_contains"
    SIZE_OVER = "size_over"
    SIZE_UNDER = "size_under"


class MatchType(Enum):
    """How to match the condition."""
    IS = ":is"
    CONTAINS = ":contains"
    MATCHES = ":matches"
    REGEX = ":regex"


@dataclass(frozen=True, slots=True)
class FilterCondition:
    """Immutable filter condition for matching emails.

    Represents a single condition in a Sieve filter rule.
    Examples:
        - Header contains "Newsletter"
        - From domain is "amazon.com"
        - Subject matches pattern
    """

    condition_type: ConditionType
    field: str  # e.g., "subject", "from", "to"
    match_type: MatchType
    value: str

    def __post_init__(self) -> None:
        """Validate condition on construction."""
        if not self.field:
            raise ValueError("Field cannot be empty")
        if not self.value:
            raise ValueError("Value cannot be empty")

    @classmethod
    def header_contains(cls, field: str, value: str) -> Self:
        """Factory method for header contains condition."""
        return cls(
            condition_type=ConditionType.HEADER_CONTAINS,
            field=field,
            match_type=MatchType.CONTAINS,
            value=value
        )

    @classmethod
    def address_domain_is(cls, field: str, domain: str) -> Self:
        """Factory method for address domain condition."""
        return cls(
            condition_type=ConditionType.ADDRESS_DOMAIN,
            field=field,
            match_type=MatchType.IS,
            value=domain
        )

    @classmethod
    def from_pattern(cls, pattern: str) -> Self:
        """Create condition from pattern string like 'from:@domain.com' or 'subject:keyword'."""
        pattern = pattern.strip()

        if pattern.startswith("from:"):
            value = pattern[5:].strip()
            if value.startswith('@'):
                # Domain pattern
                return cls.address_domain_is("from", value[1:])
            else:
                # Email or partial match
                return cls.header_contains("from", value)

        elif pattern.startswith("subject:"):
            value = pattern[8:].strip()
            return cls.header_contains("subject", value)

        else:
            # Default to subject contains
            return cls.header_contains("subject", pattern)

    def to_sieve(self) -> str:
        """Convert condition to Sieve script syntax."""
        if self.condition_type == ConditionType.ADDRESS_DOMAIN:
            return f'address :domain {self.match_type.value} "{self.field}" "{self.value}"'
        elif self.condition_type == ConditionType.HEADER_CONTAINS:
            return f'header {self.match_type.value} "{self.field}" "{self.value}"'
        elif self.condition_type == ConditionType.HEADER_IS:
            return f'header {self.match_type.value} "{self.field}" "{self.value}"'
        else:
            return f'# Unsupported condition type: {self.condition_type}'

    def __str__(self) -> str:
        return f"{self.field} {self.match_type.value} {self.value}"
