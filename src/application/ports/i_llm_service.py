"""ILLMService port - Interface for LLM/AI services."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Sequence

from src.domain.entities.email import Email
from src.domain.value_objects.email_cluster import EmailCluster
from src.domain.value_objects.email_summary import EmailSummary


class ILLMService(ABC):
    """Port interface for LLM service adapters.
    
    Implementations might include:
    - OllamaAdapter (local LLMs)
    - AnthropicAdapter (Claude API)
    - OpenAIAdapter (GPT API)
    - MockLLMAdapter (for testing)
    """

    @abstractmethod
    def analyze_emails(
        self,
        emails: Sequence[Email],
        max_sample: int = 20,
    ) -> dict[str, Any]:
        """Analyze emails and detect patterns/categories.
        
        Args:
            emails: Collection of emails to analyze
            max_sample: Maximum emails to include in analysis
            
        Returns:
            Dictionary containing:
                {
                    "categories": [
                        {
                            "name": str,
                            "description": str,
                            "patterns": list[str],
                            "suggested_folder": str,
                            "confidence": float,
                            "example_subjects": list[str]
                        },
                        ...
                    ]
                }
                
        Raises:
            LLMError: If analysis fails
            TimeoutError: If analysis times out
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Check if LLM service is available.
        
        Returns:
            True if service is healthy
        """
        pass

    @abstractmethod
    def get_model_info(self) -> dict[str, str]:
        """Get information about the LLM model.

        Returns:
            Dictionary with model details (name, version, provider, etc.)
        """
        pass

    def analyze_summaries(
        self,
        summaries: Sequence[EmailSummary],
        max_sample: int = 100,
        existing_folders: dict[str, int] | None = None,
    ) -> dict[str, Any]:
        """Analyze email summaries and detect hierarchical patterns (Master tier).

        Args:
            summaries: Collection of email summaries from worker tier
            max_sample: Maximum summaries to include in analysis
            existing_folders: Optional dict of existing folder names to email counts

        Returns:
            Dictionary containing hierarchical categories
        """
        # Default implementation for adapters that don't override
        return self.analyze_emails(
            emails=[],  # Not used in this mode
            max_sample=max_sample
        )

    def analyze_clusters(
        self,
        clusters: Sequence[EmailCluster],
        max_representatives: int = 3,
        existing_folders: dict[str, int] | None = None,
    ) -> dict[str, Any]:
        """Analyze email clusters and label them with categories (Embedding mode).

        Args:
            clusters: Collection of email clusters to analyze
            max_representatives: Maximum representative emails per cluster
            existing_folders: Optional dict of existing folder names to email counts

        Returns:
            Dictionary containing hierarchical categories
        """
        # Default implementation for adapters that don't override
        return self.analyze_emails(
            emails=[],  # Not used in this mode
            max_sample=max_representatives
        )
