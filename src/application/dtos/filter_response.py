"""FilterResponse DTO."""

from __future__ import annotations

from dataclasses import dataclass

from src.domain.entities.sieve_filter import SieveFilter


@dataclass(frozen=True, slots=True)
class FilterResponse:
    """Generic response DTO for filter operations."""

    sieve_filter: SieveFilter
    message: str
    success: bool = True
    output_path: str | None = None
