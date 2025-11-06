"""Infrastructure layer - Adapters and external dependencies."""

from .adapters import IMAPAdapter, OllamaAdapter, SieveFileAdapter
from .container import Container

__all__ = [
    "IMAPAdapter",
    "OllamaAdapter",
    "SieveFileAdapter",
    "Container",
]
