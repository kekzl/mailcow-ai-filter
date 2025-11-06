"""Infrastructure adapters - Implementations of application ports."""

from .imap_adapter import IMAPAdapter
from .ollama_adapter import OllamaAdapter
from .sieve_file_adapter import SieveFileAdapter

__all__ = [
    "IMAPAdapter",
    "OllamaAdapter",
    "SieveFileAdapter",
]
