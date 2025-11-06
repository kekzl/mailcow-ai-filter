"""Port interface for email clustering service."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

import numpy as np
from numpy.typing import NDArray

from src.domain.entities.email import Email
from src.domain.value_objects.email_cluster import EmailCluster


class IClusteringService(ABC):
    """Interface for clustering emails based on their embeddings."""

    @abstractmethod
    def cluster_emails(
        self,
        emails: Sequence[Email],
        embeddings: NDArray[np.float32],
        min_cluster_size: int = 5,
    ) -> list[EmailCluster]:
        """Cluster emails based on their embedding vectors.

        Args:
            emails: Collection of emails to cluster
            embeddings: 2D array of email embeddings (n_emails, embedding_dim)
            min_cluster_size: Minimum number of emails to form a cluster

        Returns:
            List of EmailCluster objects (excludes noise/outliers)
        """
        pass

    @abstractmethod
    def find_representative_indices(
        self,
        cluster_emails: Sequence[Email],
        cluster_embeddings: NDArray[np.float32],
        n_representatives: int = 3,
    ) -> list[int]:
        """Find indices of emails closest to cluster center.

        Args:
            cluster_emails: Emails in the cluster
            cluster_embeddings: Embeddings for emails in the cluster
            n_representatives: Number of representative emails to find

        Returns:
            List of indices of representative emails
        """
        pass
