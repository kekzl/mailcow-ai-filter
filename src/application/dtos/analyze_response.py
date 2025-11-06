"""AnalyzeEmailsResponse DTO."""

from __future__ import annotations

from dataclasses import dataclass

from src.domain.entities.sieve_filter import SieveFilter


@dataclass(frozen=True, slots=True)
class AnalyzeEmailsResponse:
    """Response DTO for email analysis use case."""

    sieve_filter: SieveFilter
    total_emails_analyzed: int
    categories_found: int
    analysis_time_seconds: float
    filter_output_path: str | None = None

    @property
    def success(self) -> bool:
        """Check if analysis was successful."""
        return self.categories_found > 0
