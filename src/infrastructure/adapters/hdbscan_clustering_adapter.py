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

    def __init__(
        self,
        min_cluster_size: int = 5,
        min_samples: int = 3,
        handle_outliers: bool = True,
        outlier_min_cluster_size: int = 3,
    ):
        """Initialize HDBSCAN clusterer.

        Args:
            min_cluster_size: Minimum number of emails to form a cluster
            min_samples: Minimum samples in neighborhood for core points
            handle_outliers: Whether to re-cluster outliers with lower thresholds
            outlier_min_cluster_size: Minimum cluster size for outlier re-clustering
        """
        self.min_cluster_size = min_cluster_size
        self.min_samples = min_samples
        self.handle_outliers = handle_outliers
        self.outlier_min_cluster_size = outlier_min_cluster_size
        logger.info(
            f"Initialized HDBSCAN clustering "
            f"(min_cluster_size={min_cluster_size}, min_samples={min_samples}, "
            f"handle_outliers={handle_outliers})"
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
            metric="euclidean",  # Works well with normalized embeddings
            cluster_selection_method="eom",  # Excess of Mass
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

        # Handle outliers by re-clustering with lower thresholds
        if self.handle_outliers and n_noise >= self.outlier_min_cluster_size:
            logger.info(f"Re-clustering {n_noise} outliers with lower thresholds...")

            # Get outlier indices
            outlier_indices = np.where(cluster_labels == -1)[0]
            outlier_emails = [emails[i] for i in outlier_indices]
            outlier_embeddings = embeddings[outlier_indices]

            # Re-cluster with more lenient parameters
            outlier_clusters = self._recluster_outliers(
                outlier_emails,
                outlier_embeddings,
                next_cluster_id=len(unique_labels),
            )

            if outlier_clusters:
                clusters.extend(outlier_clusters)
                logger.info(
                    f"Re-clustering created {len(outlier_clusters)} additional clusters "
                    f"from {sum(c.size for c in outlier_clusters)} outliers"
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

    def _recluster_outliers(
        self,
        outlier_emails: Sequence[Email],
        outlier_embeddings: NDArray[np.float32],
        next_cluster_id: int,
    ) -> list[EmailCluster]:
        """Re-cluster outliers with more lenient parameters.

        Args:
            outlier_emails: Emails marked as outliers
            outlier_embeddings: Embeddings for outlier emails
            next_cluster_id: Starting cluster ID for new clusters

        Returns:
            List of EmailCluster objects created from outliers
        """
        if len(outlier_emails) < self.outlier_min_cluster_size:
            return []

        # Use more lenient parameters for outlier re-clustering
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=self.outlier_min_cluster_size,
            min_samples=max(1, self.min_samples - 1),  # Lower min_samples
            metric="euclidean",
            cluster_selection_method="leaf",  # More lenient selection method
            prediction_data=True,
        )

        # Perform clustering on outliers
        outlier_labels = clusterer.fit_predict(outlier_embeddings)

        # Count new clusters (excluding noise label -1)
        unique_outlier_labels = set(outlier_labels)
        unique_outlier_labels.discard(-1)

        if not unique_outlier_labels:
            logger.info("Re-clustering did not create any new clusters")
            return []

        # Build EmailCluster objects from re-clustered outliers
        new_clusters = []
        for outlier_cluster_id in sorted(unique_outlier_labels):
            # Get indices of emails in this outlier cluster
            cluster_indices = np.where(outlier_labels == outlier_cluster_id)[0]
            cluster_emails = [outlier_emails[i] for i in cluster_indices]
            cluster_embeddings = outlier_embeddings[cluster_indices]

            # Find representative emails
            centroid_indices = self.find_representative_indices(
                cluster_emails,
                cluster_embeddings,
                n_representatives=min(3, len(cluster_emails)),
            )

            # Create cluster with adjusted ID
            email_cluster = EmailCluster.create(
                cluster_id=next_cluster_id + int(outlier_cluster_id),
                emails=cluster_emails,
                centroid_indices=centroid_indices,
            )
            new_clusters.append(email_cluster)

            logger.debug(
                f"Outlier cluster {next_cluster_id + outlier_cluster_id}: {len(cluster_emails)} emails"
            )

        return new_clusters
