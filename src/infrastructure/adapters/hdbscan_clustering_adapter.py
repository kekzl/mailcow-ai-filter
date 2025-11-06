"""HDBSCAN clustering adapter for email clustering."""

from __future__ import annotations

import logging
from typing import Sequence

import hdbscan
import numpy as np
from numpy.typing import NDArray
from sklearn.metrics.pairwise import cosine_distances

from src.application.ports.i_clustering_service import IClusteringService
from src.domain.entities.email import Email
from src.domain.value_objects.email_cluster import EmailCluster

logger = logging.getLogger(__name__)


class HDBSCANClusteringAdapter(IClusteringService):
    """Clustering service using HDBSCAN algorithm.

    HDBSCAN (Hierarchical Density-Based Spatial Clustering of Applications with Noise)
    automatically determines the number of clusters and handles outliers well.
    """

    def __init__(self, min_cluster_size: int = 5, min_samples: int = 3):
        """Initialize HDBSCAN clusterer.

        Args:
            min_cluster_size: Minimum number of emails to form a cluster
            min_samples: Minimum samples in neighborhood for core points
        """
        self.min_cluster_size = min_cluster_size
        self.min_samples = min_samples
        logger.info(
            f"Initialized HDBSCAN clustering "
            f"(min_cluster_size={min_cluster_size}, min_samples={min_samples})"
        )

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
        if len(emails) == 0:
            return []

        if len(emails) < min_cluster_size:
            logger.warning(
                f"Too few emails ({len(emails)}) to form clusters "
                f"(min_cluster_size={min_cluster_size}). Creating single cluster."
            )
            # Put all emails in one cluster
            return [
                EmailCluster.create(
                    cluster_id=0,
                    emails=emails,
                    centroid_indices=list(range(min(3, len(emails)))),
                )
            ]

        logger.info(f"Clustering {len(emails)} emails...")

        # Create HDBSCAN clusterer
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=max(min_cluster_size, self.min_cluster_size),
            min_samples=self.min_samples,
            metric='euclidean',  # Works well with normalized embeddings
            cluster_selection_method='eom',  # Excess of Mass
            prediction_data=True,
        )

        # Perform clustering
        cluster_labels = clusterer.fit_predict(embeddings)

        # Count clusters (excluding noise label -1)
        unique_labels = set(cluster_labels)
        unique_labels.discard(-1)  # Remove noise label
        n_clusters = len(unique_labels)
        n_noise = sum(1 for label in cluster_labels if label == -1)

        logger.info(
            f"Found {n_clusters} clusters, {n_noise} outliers "
            f"(outlier rate: {n_noise / len(emails) * 100:.1f}%)"
        )

        # Build EmailCluster objects
        clusters = []
        for cluster_id in sorted(unique_labels):
            # Get indices of emails in this cluster
            cluster_indices = np.where(cluster_labels == cluster_id)[0]
            cluster_emails = [emails[i] for i in cluster_indices]
            cluster_embeddings = embeddings[cluster_indices]

            # Find representative emails (closest to centroid)
            centroid_indices = self.find_representative_indices(
                cluster_emails,
                cluster_embeddings,
                n_representatives=min(3, len(cluster_emails)),
            )

            # Create cluster
            email_cluster = EmailCluster.create(
                cluster_id=int(cluster_id),
                emails=cluster_emails,
                centroid_indices=centroid_indices,
            )
            clusters.append(email_cluster)

            logger.debug(
                f"Cluster {cluster_id}: {len(cluster_emails)} emails, "
                f"representatives: {centroid_indices[:3]}"
            )

        return clusters

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
        if len(cluster_emails) == 0:
            return []

        if len(cluster_emails) <= n_representatives:
            return list(range(len(cluster_emails)))

        # Compute cluster centroid (mean of all embeddings)
        centroid = cluster_embeddings.mean(axis=0, keepdims=True)

        # Compute distances from each email to centroid
        # Using cosine distance (works well with normalized embeddings)
        distances = cosine_distances(cluster_embeddings, centroid).flatten()

        # Find indices of emails with smallest distances
        representative_indices = np.argsort(distances)[:n_representatives]

        return representative_indices.tolist()
