"""Dependency Injection Container."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

from src.application.dtos.analyze_request import AnalyzeEmailsRequest
from src.application.use_cases.analyze_emails_use_case import AnalyzeEmailsUseCase
from src.domain.services.filter_generator import FilterGenerator
from src.infrastructure.adapters.hdbscan_clustering_adapter import (
    HDBSCANClusteringAdapter,
)
from src.infrastructure.adapters.imap_adapter import IMAPAdapter
from src.infrastructure.adapters.ollama_adapter import OllamaAdapter
from src.infrastructure.adapters.ollama_email_summarizer import OllamaEmailSummarizer
from src.infrastructure.adapters.sentence_transformer_adapter import (
    SentenceTransformerAdapter,
)
from src.infrastructure.adapters.sieve_file_adapter import SieveFileAdapter

logger = logging.getLogger(__name__)


class Container:
    """Dependency injection container for wiring components."""

    def __init__(self, config: dict) -> None:
        """Initialize container with configuration.

        Args:
            config: Application configuration dictionary
        """
        self.config = config
        self._email_fetcher = None
        self._llm_service = None
        self._email_summarizer = None
        self._embedding_service = None
        self._clustering_service = None
        self._filter_repository = None
        self._filter_generator = None
        self._analyze_emails_use_case = None

        logger.info("Initialized dependency injection container")

    def email_fetcher(self) -> IMAPAdapter:
        """Get or create email fetcher adapter.

        Returns:
            Configured IMAPAdapter instance
        """
        if self._email_fetcher is None:
            imap_config = self.config.get("imap", {})
            self._email_fetcher = IMAPAdapter(
                server=imap_config.get("server", "localhost"),
                username=imap_config.get("username", ""),
                password=imap_config.get("password", ""),
                use_ssl=imap_config.get("use_ssl", True),
                port=imap_config.get("port"),
            )
            logger.info("Created IMAPAdapter instance")

        return self._email_fetcher

    def llm_service(self) -> OllamaAdapter:
        """Get or create LLM service adapter (master model).

        Returns:
            Configured OllamaAdapter instance for master tier
        """
        if self._llm_service is None:
            ai_config = self.config.get("ai", {})
            master_model = ai_config.get("master_model") or ai_config.get(
                "model", "qwen3:14b"
            )

            # Read AI generation settings
            temperature = ai_config.get("temperature", 0.7)
            num_predict = ai_config.get("num_predict", 6000)
            top_p = ai_config.get("top_p", 0.9)

            self._llm_service = OllamaAdapter(
                model=master_model,
                base_url=ai_config.get("base_url", "http://localhost:11434"),
                temperature=temperature,
                num_predict=num_predict,
                top_p=top_p,
            )
            logger.info(
                f"Created OllamaAdapter (master model: {master_model}, temp={temperature})"
            )

        return self._llm_service

    def email_summarizer(self) -> OllamaEmailSummarizer | None:
        """Get or create email summarizer (worker model).

        Returns:
            Configured OllamaEmailSummarizer instance or None if disabled
        """
        if self._email_summarizer is None:
            ai_config = self.config.get("ai", {})

            # Check if hierarchical mode is enabled
            use_hierarchical = ai_config.get("use_hierarchical", True)

            if not use_hierarchical:
                logger.info("Hierarchical mode disabled, using simple mode")
                return None

            worker_model = ai_config.get("worker_model", "qwen3:4b")

            self._email_summarizer = OllamaEmailSummarizer(
                model=worker_model,
                base_url=ai_config.get("base_url", "http://localhost:11434"),
            )
            logger.info(f"Created OllamaEmailSummarizer (worker model: {worker_model})")

        return self._email_summarizer

    def embedding_service(self) -> SentenceTransformerAdapter | None:
        """Get or create embedding service.

        Returns:
            Configured SentenceTransformerAdapter instance or None if disabled
        """
        if self._embedding_service is None:
            ai_config = self.config.get("ai", {})

            # Check if embedding mode is enabled
            use_embedding = ai_config.get("use_embedding", False)

            if not use_embedding:
                logger.info("Embedding mode disabled")
                return None

            # Read embedding model from config
            embedding_config = self.config.get("embedding", {})
            model_name = embedding_config.get("model", "all-MiniLM-L6-v2")

            self._embedding_service = SentenceTransformerAdapter(model_name=model_name)
            logger.info(f"Created SentenceTransformerAdapter (model: {model_name})")

        return self._embedding_service

    def clustering_service(self) -> HDBSCANClusteringAdapter | None:
        """Get or create clustering service.

        Returns:
            Configured HDBSCANClusteringAdapter instance or None if disabled
        """
        if self._clustering_service is None:
            ai_config = self.config.get("ai", {})

            # Check if embedding mode is enabled
            use_embedding = ai_config.get("use_embedding", False)

            if not use_embedding:
                logger.info("Clustering service disabled")
                return None

            # Read clustering parameters from config
            clustering_config = self.config.get("clustering", {})
            min_cluster_size = clustering_config.get("min_cluster_size", 5)
            min_samples = clustering_config.get("min_samples", 2)
            handle_outliers = clustering_config.get("handle_outliers", True)
            outlier_min_cluster_size = clustering_config.get(
                "outlier_min_cluster_size", 3
            )

            self._clustering_service = HDBSCANClusteringAdapter(
                min_cluster_size=min_cluster_size,
                min_samples=min_samples,
                handle_outliers=handle_outliers,
                outlier_min_cluster_size=outlier_min_cluster_size,
            )
            logger.info(
                f"Created HDBSCANClusteringAdapter (min_cluster_size={min_cluster_size}, "
                f"min_samples={min_samples}, handle_outliers={handle_outliers})"
            )

        return self._clustering_service

    def filter_repository(self) -> SieveFileAdapter:
        """Get or create filter repository adapter.

        Returns:
            Configured SieveFileAdapter instance
        """
        if self._filter_repository is None:
            sieve_config = self.config.get("sieve", {})
            output_file = sieve_config.get("output_file", "/app/output/generated.sieve")
            # Extract directory from output_file
            import os

            output_dir = os.path.dirname(output_file)

            self._filter_repository = SieveFileAdapter(default_output_dir=output_dir)
            logger.info("Created SieveFileAdapter instance")

        return self._filter_repository

    def filter_generator(self) -> FilterGenerator:
        """Get or create filter generator domain service.

        Returns:
            FilterGenerator instance
        """
        if self._filter_generator is None:
            self._filter_generator = FilterGenerator(min_confidence=0.5)
            logger.info("Created FilterGenerator instance")

        return self._filter_generator

    def analyze_emails_use_case(self) -> AnalyzeEmailsUseCase:
        """Get or create analyze emails use case.

        Returns:
            Configured AnalyzeEmailsUseCase instance
        """
        if self._analyze_emails_use_case is None:
            email_summarizer = self.email_summarizer()
            embedding_service = self.embedding_service()
            clustering_service = self.clustering_service()

            max_parallel_workers = self.config["ai"].get("max_parallel_workers", 3)

            self._analyze_emails_use_case = AnalyzeEmailsUseCase(
                email_fetcher=self.email_fetcher(),
                llm_service=self.llm_service(),
                filter_repository=self.filter_repository(),
                filter_generator=self.filter_generator(),
                email_summarizer=email_summarizer,
                max_parallel_workers=max_parallel_workers,
                embedding_service=embedding_service,
                clustering_service=clustering_service,
            )

            # Determine mode based on available services
            if embedding_service and clustering_service:
                mode = "embedding"
            elif email_summarizer:
                mode = "hierarchical"
            else:
                mode = "simple"

            logger.info(f"Created AnalyzeEmailsUseCase instance ({mode} mode)")

        return self._analyze_emails_use_case

    def create_analyze_request(self) -> AnalyzeEmailsRequest:
        """Create analyze request from configuration.

        Returns:
            Configured AnalyzeEmailsRequest DTO
        """
        analysis_config = self.config.get("analysis", {})
        ai_config = self.config.get("ai", {})

        # Calculate since_date from months_back
        months_back = analysis_config.get("months_back", 12)
        since_date = datetime.now() - timedelta(days=months_back * 30)

        return AnalyzeEmailsRequest(
            folder="INBOX",
            since_date=since_date,
            max_emails=ai_config.get("max_emails_to_analyze", 100),
            exclude_folders=analysis_config.get("exclude_folders", []),
            min_category_size=analysis_config.get("min_category_size", 5),
            sample_from_folders=ai_config.get("sample_from_folders", True),
        )
