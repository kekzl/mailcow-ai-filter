"""Port interface for email summarization service."""

from __future__ import annotations

from typing import Protocol, Sequence

from src.domain.entities.email import Email
from src.domain.value_objects.email_summary import EmailSummary


class IEmailSummarizer(Protocol):
    """Port for summarizing individual emails.

    This is the worker tier in the two-tier architecture.
    Uses a fast, efficient model to extract key information
    from each email.
    """

    def summarize(self, email: Email) -> EmailSummary:
        """Summarize a single email.

        Args:
            email: Email entity to summarize

        Returns:
            EmailSummary with extracted information

        Raises:
            Exception: If summarization fails
        """
        ...

    def summarize_batch(
        self,
        emails: Sequence[Email],
        max_parallel: int = 10
    ) -> list[EmailSummary]:
        """Summarize multiple emails in parallel.

        Args:
            emails: Collection of emails to summarize
            max_parallel: Maximum number of parallel requests

        Returns:
            List of email summaries

        Raises:
            Exception: If batch summarization fails
        """
        ...
