"""Sentence Transformer adapter for email embedding."""

from __future__ import annotations

import logging
from typing import Sequence

import numpy as np
from numpy.typing import NDArray
from sentence_transformers import SentenceTransformer

from src.application.ports.i_embedding_service import IEmbeddingService
from src.domain.entities.email import Email

logger = logging.getLogger(__name__)


class SentenceTransformerAdapter(IEmbeddingService):
    """Embedding service using sentence-transformers library.

    Uses lightweight models optimized for semantic similarity.
    Default model: all-MiniLM-L6-v2 (384 dimensions, 80MB, fast)
    """

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """Initialize sentence transformer model.

        Args:
            model_name: HuggingFace model name (default: all-MiniLM-L6-v2)
        """
        self.model_name = model_name
        logger.info(f"Loading sentence transformer model: {model_name}")

        # Load model (downloads on first use, then cached)
        self.model = SentenceTransformer(model_name)

        logger.info(
            f"Loaded model {model_name} "
            f"(embedding_dim={self.model.get_sentence_embedding_dimension()})"
        )

    def encode_emails(self, emails: Sequence[Email]) -> NDArray[np.float32]:
        """Convert emails to vector embeddings.

        Args:
            emails: Collection of emails to encode

        Returns:
            2D numpy array of shape (n_emails, embedding_dim)
        """
        if not emails:
            return np.array([], dtype=np.float32).reshape(0, self.model.get_sentence_embedding_dimension())

        logger.info(f"Encoding {len(emails)} emails to embeddings...")

        # Prepare text: combine subject and body snippet
        texts = [
            f"Subject: {email.subject}\nFrom: {email.sender.value}\n{email.body[:500]}"
            for email in emails
        ]

        # Encode in batch (much faster than one-by-one)
        embeddings = self.model.encode(
            texts,
            batch_size=32,
            show_progress_bar=len(emails) > 100,
            convert_to_numpy=True,
            normalize_embeddings=True,  # L2 normalization for cosine similarity
        )

        logger.info(f"Generated embeddings with shape {embeddings.shape}")
        return embeddings.astype(np.float32)

    def encode_text(self, text: str) -> NDArray[np.float32]:
        """Convert a single text string to an embedding vector.

        Args:
            text: Text to encode

        Returns:
            1D numpy array of shape (embedding_dim,)
        """
        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return embedding.astype(np.float32)
