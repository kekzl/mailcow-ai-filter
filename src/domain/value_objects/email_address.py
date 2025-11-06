"""EmailAddress value object with validation."""

import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EmailAddress:
    """Email address value object with domain validation.

    Immutable value object representing an email address.
    Ensures all email addresses in the system are valid.
    """

    value: str

    def __post_init__(self) -> None:
        """Validate email address format on construction."""
        if not self._is_valid(self.value):
            raise ValueError(f"Invalid email address: {self.value}")

    @staticmethod
    def _is_valid(email: str) -> bool:
        """Check if email format is valid using RFC 5322 simplified regex."""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    @property
    def domain(self) -> str:
        """Extract domain from email address."""
        return self.value.split("@")[1] if "@" in self.value else ""

    @property
    def local_part(self) -> str:
        """Extract local part (before @) from email address."""
        return self.value.split("@")[0] if "@" in self.value else self.value

    def matches_domain(self, domain: str) -> bool:
        """Check if email address belongs to specified domain."""
        return self.domain.lower() == domain.lower()

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"EmailAddress('{self.value}')"
