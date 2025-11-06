"""Port interface for email embedding service."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

import numpy as np
from numpy.typing import NDArray

from src.domain.entities.email import Email


class IEmbeddingService(ABC):
    """Interface for converting emails to vector embeddings."""

    @abstractmethod
    def encode_emails(self, emails: Sequence[Email]) -> NDArray[np.float32]:
        """Convert emails to vector embeddings.

        Args:
            emails: Collection of emails to encode

        Returns:
            2D numpy array of shape (n_emails, embedding_dim)
            where each row is the embedding vector for an email
        """
        pass

    @abstractmethod
    def encode_text(self, text: str) -> NDArray[np.float32]:
        """Convert a single text string to an embedding vector.

        Args:
            text: Text to encode

        Returns:
            1D numpy array of shape (embedding_dim,)
        """
        pass
