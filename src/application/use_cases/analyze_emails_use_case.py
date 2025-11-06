"""AnalyzeEmailsUseCase - Main email analysis workflow."""

from __future__ import annotations

import logging
import time

from src.application.dtos.analyze_request import AnalyzeEmailsRequest
from src.application.dtos.analyze_response import AnalyzeEmailsResponse
from src.application.ports.i_clustering_service import IClusteringService
from src.application.ports.i_email_fetcher import IEmailFetcher
from src.application.ports.i_email_summarizer import IEmailSummarizer
from src.application.ports.i_embedding_service import IEmbeddingService
from src.application.ports.i_filter_repository import IFilterRepository
from src.application.ports.i_llm_service import ILLMService
from src.domain.services.filter_generator import FilterGenerator

logger = logging.getLogger(__name__)


class AnalyzeEmailsUseCase:
    """Use case for analyzing emails and generating filters.

    Supports three modes:

    **Simple mode** (legacy):
    1. Fetch emails from email server
    2. Analyze sample with LLM
    3. Generate filters from AI analysis

    **Hierarchical mode** (two-tier):
    1. Fetch emails from email server
    2. Summarize each email with worker model (fast, parallel)
    3. Analyze all summaries with master model (smart patterns)
    4. Generate hierarchical filters

    **Embedding mode** (ML-based clustering):
    1. Fetch emails from email server
    2. Generate embeddings for all emails
    3. Cluster similar emails using HDBSCAN
    4. Label each cluster with master model
    5. Generate hierarchical filters
    """

    def __init__(
        self,
        email_fetcher: IEmailFetcher,
        llm_service: ILLMService,
        filter_repository: IFilterRepository,
        filter_generator: FilterGenerator,
        email_summarizer: IEmailSummarizer | None = None,
        max_parallel_workers: int = 3,
        embedding_service: IEmbeddingService | None = None,
        clustering_service: IClusteringService | None = None,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            email_fetcher: Port for fetching emails
            llm_service: Port for AI analysis (master model)
            filter_repository: Port for saving filters
            filter_generator: Domain service for filter generation
            email_summarizer: Optional worker model for two-tier mode
            max_parallel_workers: Maximum parallel workers for batch summarization
            embedding_service: Optional embedding service for embedding mode
            clustering_service: Optional clustering service for embedding mode
        """
        self.email_fetcher = email_fetcher
        self.llm_service = llm_service
        self.filter_repository = filter_repository
        self.filter_generator = filter_generator
        self.email_summarizer = email_summarizer
        self.max_parallel_workers = max_parallel_workers
        self.embedding_service = embedding_service
        self.clustering_service = clustering_service

        # Determine analysis mode based on available services
        # Priority: Embedding > Hierarchical > Simple
        if embedding_service and clustering_service:
            self.analysis_mode = "embedding"
        elif email_summarizer:
            self.analysis_mode = "hierarchical"
        else:
            self.analysis_mode = "simple"

    def execute(self, request: AnalyzeEmailsRequest) -> AnalyzeEmailsResponse:
        """Execute the email analysis workflow.
        
        Args:
            request: Analysis request parameters
            
        Returns:
            Analysis response with generated filter
            
        Raises:
            ValueError: If request is invalid
            ConnectionError: If email server connection fails
            Exception: For other errors during execution
        """
        start_time = time.time()
        
        logger.info(
            f"Starting email analysis: max_emails={request.max_emails}, "
            f"exclude_folders={request.exclude_folders}"
        )

        # Step 1: Fetch existing folder structure
        logger.info("Fetching existing folder structure from server...")
        self.email_fetcher.connect()

        try:
            # Get existing folders and their email counts
            existing_folders = self._fetch_folder_structure()
            logger.info(f"Found {len(existing_folders)} existing folders")

            # Step 2: Fetch emails
            logger.info("Fetching emails from server...")
            emails = self.email_fetcher.fetch_emails(
                folder=request.folder,
                since_date=request.since_date,
                max_emails=request.max_emails,
                exclude_folders=request.exclude_folders,
            )
            
            logger.info(f"Fetched {len(emails)} emails")
            
            if not emails:
                raise ValueError("No emails found to analyze")

            # Step 3: Analyze emails using appropriate mode
            if self.analysis_mode == "embedding":
                # Embedding-based clustering mode
                logger.info("Using embedding-based clustering mode")

                # Step 2a: Generate embeddings for all emails
                logger.info(f"Generating embeddings for {len(emails)} emails...")
                embeddings = self.embedding_service.encode_emails(emails)
                logger.info(f"Generated embeddings with shape {embeddings.shape}")

                # Step 2b: Cluster similar emails
                logger.info("Clustering emails based on embeddings...")
                clusters = self.clustering_service.cluster_emails(
                    emails=emails,
                    embeddings=embeddings,
                    min_cluster_size=5,
                )
                logger.info(f"Found {len(clusters)} clusters")

                # Step 2c: Analyze clusters with master model
                logger.info("Labeling clusters with master model...")
                ai_response = self.llm_service.analyze_clusters(
                    clusters=clusters,
                    max_representatives=5,  # Increased for more context per cluster
                    existing_folders=existing_folders,
                )

            elif self.analysis_mode == "hierarchical":
                # Two-tier hierarchical mode
                logger.info("Using hierarchical two-tier analysis mode")

                # Step 2a: Summarize each email with worker model
                logger.info(f"Summarizing {len(emails)} emails with worker model...")
                summaries = self.email_summarizer.summarize_batch(
                    emails=emails,
                    max_parallel=self.max_parallel_workers,
                )
                logger.info(f"Created {len(summaries)} email summaries")

                # Step 2b: Analyze summaries with master model
                logger.info("Analyzing summaries with master model...")
                ai_response = self.llm_service.analyze_summaries(
                    summaries=summaries,
                    max_sample=len(summaries),  # Use all summaries
                    existing_folders=existing_folders,
                )

            else:
                # Simple mode (legacy)
                logger.info("Using simple analysis mode")
                logger.info("Analyzing emails with AI...")
                ai_response = self.llm_service.analyze_emails(
                    emails=emails,
                    max_sample=min(20, len(emails)),
                )

            logger.debug(f"AI response: {ai_response}")

            # Step 3: Generate filter from AI analysis
            logger.info("Generating Sieve filter from patterns...")
            sieve_filter = self.filter_generator.generate_filter_from_raw_response(
                ai_response
            )
            
            logger.info(
                f"Generated filter with {len(sieve_filter.rules)} rules"
            )

            # Step 4: Save filter (if output path provided)
            output_path = None
            if hasattr(request, 'output_file'):
                output_path = self.filter_repository.save(
                    sieve_filter, 
                    getattr(request, 'output_file', '/app/output/generated.sieve')
                )
                logger.info(f"Saved filter to {output_path}")

            analysis_time = time.time() - start_time
            
            return AnalyzeEmailsResponse(
                sieve_filter=sieve_filter,
                total_emails_analyzed=len(emails),
                categories_found=len(sieve_filter.rules),
                analysis_time_seconds=analysis_time,
                filter_output_path=output_path,
            )

        finally:
            self.email_fetcher.disconnect()
            logger.info(
                f"Email analysis completed in {time.time() - start_time:.2f}s"
            )

    def _fetch_folder_structure(self) -> dict[str, int]:
        """Fetch existing folder structure from email server.

        Returns:
            Dictionary mapping folder names to email counts
        """
        folder_structure = {}

        try:
            # Get list of all folders
            folders = self.email_fetcher.list_folders()

            # Get email count for each folder
            for folder in folders:
                try:
                    count = self.email_fetcher.get_folder_count(folder)
                    folder_structure[folder] = count
                except Exception as e:
                    logger.warning(f"Failed to get count for folder {folder}: {e}")
                    folder_structure[folder] = 0

        except Exception as e:
            logger.warning(f"Failed to fetch folder structure: {e}")

        return folder_structure
