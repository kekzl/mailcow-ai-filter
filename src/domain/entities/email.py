"""Email entity - Aggregate root for email messages."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Self

from ..value_objects.email_address import EmailAddress
from ..value_objects.email_pattern import EmailPattern


@dataclass
class Email:
    """Email aggregate root representing a single email message.

    This is the main entity for email management with identity (id).
    Contains all email data and business logic for email analysis.
    """

    id: str
    sender: EmailAddress
    recipients: tuple[EmailAddress, ...]
    subject: str
    body: str
    headers: dict[str, str]
    received_at: datetime
    folder: str = "INBOX"
    message_id: str | None = None
    has_attachments: bool = False
    _domain_events: list = field(default_factory=list, init=False, repr=False)

    @classmethod
    def create(
        cls,
        sender: str,
        recipients: list[str],
        subject: str,
        body: str,
        headers: dict[str, str] | None = None,
        received_at: datetime | None = None,
        folder: str = "INBOX",
        message_id: str | None = None,
        has_attachments: bool = False,
    ) -> Self:
        """Factory method to create Email with validation.

        Args:
            sender: Sender email address
            recipients: List of recipient email addresses
            subject: Email subject
            body: Email body content
            headers: Optional email headers
            received_at: When email was received
            folder: Current folder location
            message_id: Optional message ID
            has_attachments: Whether email has attachments

        Returns:
            New Email entity

        Raises:
            ValueError: If validation fails
        """
        return cls(
            id=str(uuid.uuid4()),
            sender=EmailAddress(sender),
            recipients=tuple(EmailAddress(r) for r in recipients),
            subject=subject,
            body=body,
            headers=headers or {},
            received_at=received_at or datetime.now(),
            folder=folder,
            message_id=message_id,
            has_attachments=has_attachments,
        )

    def matches_pattern(self, pattern: EmailPattern) -> bool:
        """Check if email matches a specific pattern.

        Domain logic for pattern matching.

        Args:
            pattern: Pattern to match against

        Returns:
            True if email matches pattern
        """
        if pattern.pattern_type == "domain":
            return self.sender.matches_domain(pattern.value)
        elif pattern.pattern_type == "subject":
            return pattern.value.lower() in self.subject.lower()
        elif pattern.pattern_type == "sender":
            return pattern.value.lower() in self.sender.value.lower()
        else:
            return False

    def is_from_domain(self, domain: str) -> bool:
        """Check if email is from specified domain."""
        return self.sender.matches_domain(domain)

    def contains_keyword_in_subject(self, keyword: str) -> bool:
        """Check if subject contains keyword (case-insensitive)."""
        return keyword.lower() in self.subject.lower()

    def contains_keyword_in_body(self, keyword: str) -> bool:
        """Check if body contains keyword (case-insensitive)."""
        return keyword.lower() in self.body.lower()

    def get_domain_events(self) -> list:
        """Get and clear domain events."""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events

    def __eq__(self, other: object) -> bool:
        """Compare emails by ID."""
        if not isinstance(other, Email):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)

    def __str__(self) -> str:
        return f"Email(from={self.sender}, subject='{self.subject[:50]}...')"

    def __repr__(self) -> str:
        return f"Email(id='{self.id}', sender='{self.sender.value}', subject='{self.subject[:30]}...')"
