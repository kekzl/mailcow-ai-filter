"""EmailPattern value object for detected patterns in emails."""

from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True, slots=True)
class EmailPattern:
    """Immutable email pattern detected by AI analysis.

    Represents a pattern found in a group of similar emails.
    Used to generate filter conditions.
    """

    pattern_type: str  # "from", "subject", "domain", etc.
    value: str
    confidence: float
    sample_count: int = 0

    def __post_init__(self) -> None:
        """Validate pattern on construction."""
        if not self.pattern_type:
            raise ValueError("Pattern type cannot be empty")
        if not self.value:
            raise ValueError("Pattern value cannot be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0 and 1")
        if self.sample_count < 0:
            raise ValueError("Sample count cannot be negative")

    @classmethod
    def from_domain(cls, domain: str, confidence: float, sample_count: int = 0) -> Self:
        """Factory method to create domain pattern."""
        return cls(
            pattern_type="domain",
            value=domain,
            confidence=confidence,
            sample_count=sample_count
        )

    @classmethod
    def from_subject_keyword(cls, keyword: str, confidence: float, sample_count: int = 0) -> Self:
        """Factory method to create subject keyword pattern."""
        return cls(
            pattern_type="subject",
            value=keyword,
            confidence=confidence,
            sample_count=sample_count
        )

    @classmethod
    def from_sender(cls, sender: str, confidence: float, sample_count: int = 0) -> Self:
        """Factory method to create sender pattern."""
        return cls(
            pattern_type="sender",
            value=sender,
            confidence=confidence,
            sample_count=sample_count
        )

    def to_filter_string(self) -> str:
        """Convert pattern to filter string format (e.g., 'from:@domain.com')."""
        if self.pattern_type == "domain":
            return f"from:@{self.value}"
        elif self.pattern_type == "subject":
            return f"subject:{self.value}"
        elif self.pattern_type == "sender":
            return f"from:{self.value}"
        else:
            return f"{self.pattern_type}:{self.value}"

    def is_high_confidence(self, threshold: float = 0.8) -> bool:
        """Check if pattern has high confidence above threshold."""
        return self.confidence >= threshold

    def __str__(self) -> str:
        return f"{self.pattern_type}:{self.value} ({self.confidence:.0%})"

    def __repr__(self) -> str:
        return f"EmailPattern(type='{self.pattern_type}', value='{self.value}', confidence={self.confidence})"
