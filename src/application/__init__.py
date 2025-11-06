"""Application layer - Use cases, ports, and DTOs."""

from .dtos import AnalyzeEmailsRequest, AnalyzeEmailsResponse, FilterResponse
from .ports import IEmailFetcher, IFilterRepository, ILLMService
from .use_cases import AnalyzeEmailsUseCase

__all__ = [
    # Ports
    "IEmailFetcher",
    "ILLMService",
    "IFilterRepository",
    # DTOs
    "AnalyzeEmailsRequest",
    "AnalyzeEmailsResponse",
    "FilterResponse",
    # Use Cases
    "AnalyzeEmailsUseCase",
]
