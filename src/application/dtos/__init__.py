"""Application DTOs - Data Transfer Objects for use case requests/responses."""

from .analyze_request import AnalyzeEmailsRequest
from .analyze_response import AnalyzeEmailsResponse
from .filter_response import FilterResponse

__all__ = [
    "AnalyzeEmailsRequest",
    "AnalyzeEmailsResponse",
    "FilterResponse",
]
