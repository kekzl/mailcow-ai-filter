"""Email summary value object."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class EmailSummary:
    """Immutable summary of an email for pattern analysis.

    This compact representation is used by the master AI model
    to analyze patterns across many emails efficiently.
    """

    email_id: str
    sender_domain: str
    category: str  # Dynamic category determined by worker model (e.g., "CI/CD", "Orders", "Birthdays")
    topic: str  # Brief topic description
    keywords: tuple[str, ...]  # Key terms from subject/body
    folder: str
    received_at: datetime

    @classmethod
    def create(
        cls,
        email_id: str,
        sender_domain: str,
        category: str,
        topic: str,
        keywords: list[str],
        folder: str,
        received_at: datetime,
    ) -> "EmailSummary":
        """Factory method to create EmailSummary with validation.

        Args:
            email_id: Unique email identifier
            sender_domain: Domain of the sender
            category: Dynamic category (e.g., "CI/CD", "Orders", "Newsletter")
            topic: Brief description of email topic
            keywords: Important keywords
            folder: Current folder
            received_at: When email was received

        Returns:
            New EmailSummary instance
        """
        # Normalize category - capitalize first letter of each word
        category = category.strip().title() if category else "Uncategorized"

        return cls(
            email_id=email_id,
            sender_domain=sender_domain,
            category=category,
            topic=topic,
            keywords=tuple(keywords[:10]),  # Limit to 10 keywords
            folder=folder,
            received_at=received_at,
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for AI processing."""
        return {
            "sender_domain": self.sender_domain,
            "category": self.category,
            "topic": self.topic,
            "keywords": list(self.keywords),
        }

    def __str__(self) -> str:
        return f"EmailSummary(domain={self.sender_domain}, category={self.category}, topic={self.topic[:30]}...)"
