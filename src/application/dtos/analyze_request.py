"""AnalyzeEmailsRequest DTO."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class AnalyzeEmailsRequest:
    """Request DTO for email analysis use case."""

    folder: str = "INBOX"
    since_date: datetime | None = None
    max_emails: int = 100
    exclude_folders: list[str] | None = None
    min_category_size: int = 5
    sample_from_folders: bool = True

    def __post_init__(self) -> None:
        if self.max_emails <= 0:
            raise ValueError("max_emails must be positive")
        if self.min_category_size <= 0:
            raise ValueError("min_category_size must be positive")
