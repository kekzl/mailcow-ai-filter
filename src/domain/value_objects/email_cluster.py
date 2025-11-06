"""Email Cluster Value Object."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from src.domain.entities.email import Email


@dataclass(frozen=True)
class EmailCluster:
    """Represents a cluster of similar emails.

    Attributes:
        cluster_id: Unique identifier for the cluster
        emails: Collection of emails in this cluster
        centroid_indices: Indices of emails closest to cluster center
        size: Number of emails in the cluster
    """

    cluster_id: int
    emails: tuple[Email, ...]  # Immutable tuple for frozen dataclass
    centroid_indices: tuple[int, ...]  # Indices of representative emails

    @classmethod
    def create(
        cls,
        cluster_id: int,
        emails: Sequence[Email],
        centroid_indices: Sequence[int] | None = None,
    ) -> EmailCluster:
        """Create an EmailCluster instance.

        Args:
            cluster_id: Unique identifier for the cluster
            emails: Collection of emails in this cluster
            centroid_indices: Indices of representative emails (defaults to first 3)

        Returns:
            EmailCluster instance
        """
        if not emails:
            raise ValueError("Email cluster cannot be empty")

        # Default to first 3 emails if no centroids specified
        if centroid_indices is None:
            centroid_indices = tuple(range(min(3, len(emails))))

        return cls(
            cluster_id=cluster_id,
            emails=tuple(emails),
            centroid_indices=tuple(centroid_indices),
        )

    @property
    def size(self) -> int:
        """Get the number of emails in the cluster."""
        return len(self.emails)

    @property
    def representative_emails(self) -> list[Email]:
        """Get representative emails (closest to cluster center)."""
        return [self.emails[i] for i in self.centroid_indices if i < len(self.emails)]

    def __repr__(self) -> str:
        """String representation of the cluster."""
        return f"EmailCluster(id={self.cluster_id}, size={self.size})"
