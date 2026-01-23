"""FilterCondition value object for Sieve filter conditions."""

from dataclasses import dataclass
from enum import Enum
from typing import Self

# List of invalid/placeholder domains that should be rejected
INVALID_DOMAINS = {
    "example.com",
    "example.org",
    "example.net",
    "test.com",
    "test.org",
    "test.net",
    "unsorted.com",
    "random.com",
    "misc.com",
    "placeholder.com",
    "dummy.com",
    "localhost",
    "127.0.0.1",
}

# List of overly generic domains that might cause false positives
GENERIC_DOMAINS = {
    "email.com",
    "mail.com",
    "app.com",
    "security.com",
    "bank.com",
    "bank.de",
    "shop.com",
    "store.com",
}


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
            value=value,
        )

    @classmethod
    def address_domain_is(cls, field: str, domain: str) -> Self:
        """Factory method for address domain condition."""
        # Validate domain before creating condition
        if not cls.is_valid_domain(domain):
            raise ValueError(f"Invalid or placeholder domain: {domain}")
        return cls(
            condition_type=ConditionType.ADDRESS_DOMAIN,
            field=field,
            match_type=MatchType.IS,
            value=domain,
        )

    @staticmethod
    def is_valid_domain(domain: str) -> bool:
        """Check if domain is valid (not placeholder or overly generic).

        Args:
            domain: Domain name to validate

        Returns:
            True if domain is valid and specific enough
        """
        domain_lower = domain.lower().strip()

        # Check against invalid/placeholder domains
        if domain_lower in INVALID_DOMAINS:
            return False

        # Check against overly generic domains
        if domain_lower in GENERIC_DOMAINS:
            return False

        # Domain should have at least one dot (e.g., amazon.com)
        if "." not in domain_lower:
            return False

        # Domain should not be empty
        if not domain_lower:
            return False

        return True

    @classmethod
    def from_pattern(cls, pattern: str) -> Self:
        """Create condition from pattern string like 'from:@domain.com' or 'subject:keyword'.

        NOTE: For patterns with comma-separated values like 'subject:word1,word2',
        use from_pattern_multi() to get multiple conditions with OR logic.
        """
        pattern = pattern.strip()

        if pattern.startswith("from:"):
            value = pattern[5:].strip()
            if value.startswith("@"):
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

    @classmethod
    def from_pattern_multi(cls, pattern: str) -> list[Self]:
        """Create one or more conditions from pattern, handling comma-separated values.

        Examples:
            "subject:order" -> [FilterCondition(subject contains "order")]
            "subject:order,bestellt" -> [FilterCondition(subject contains "order"),
                                          FilterCondition(subject contains "bestellt")]
            "from:@domain.com" -> [FilterCondition(from domain is "domain.com")]

        Returns:
            List of FilterCondition objects (may contain single or multiple conditions)
        """
        pattern = pattern.strip()

        # Handle from: patterns (no comma splitting for from patterns)
        if pattern.startswith("from:"):
            return [cls.from_pattern(pattern)]

        # Handle subject: patterns with potential comma separation
        if pattern.startswith("subject:"):
            value = pattern[8:].strip()
            # Check if value contains commas (OR logic)
            if "," in value:
                keywords = [kw.strip() for kw in value.split(",") if kw.strip()]
                return [cls.header_contains("subject", kw) for kw in keywords]
            else:
                return [cls.header_contains("subject", value)]

        # Default to subject contains
        return [cls.header_contains("subject", pattern)]

    def to_sieve(self) -> str:
        """Convert condition to Sieve script syntax."""
        if self.condition_type == ConditionType.ADDRESS_DOMAIN:
            return (
                f'address :domain {self.match_type.value} "{self.field}" "{self.value}"'
            )
        elif self.condition_type == ConditionType.HEADER_CONTAINS:
            return f'header {self.match_type.value} "{self.field}" "{self.value}"'
        elif self.condition_type == ConditionType.HEADER_IS:
            return f'header {self.match_type.value} "{self.field}" "{self.value}"'
        else:
            return f"# Unsupported condition type: {self.condition_type}"

    def __str__(self) -> str:
        return f"{self.field} {self.match_type.value} {self.value}"
