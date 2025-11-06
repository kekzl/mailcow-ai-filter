"""Application ports - Interfaces for infrastructure adapters."""

from .i_email_fetcher import IEmailFetcher
from .i_filter_repository import IFilterRepository
from .i_llm_service import ILLMService

__all__ = [
    "IEmailFetcher",
    "ILLMService",
    "IFilterRepository",
]
