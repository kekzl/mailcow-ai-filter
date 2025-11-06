"""IFilterRepository port - Interface for filter persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.entities.sieve_filter import SieveFilter


class IFilterRepository(ABC):
    """Port interface for filter repository adapters.
    
    Implementations might include:
    - SieveFileAdapter (save to .sieve files)
    - DatabaseAdapter (save to database)
    - MailcowAPIAdapter (upload to Mailcow)
    - MockRepositoryAdapter (for testing)
    """

    @abstractmethod
    def save(self, sieve_filter: SieveFilter, output_path: str) -> str:
        """Save filter to repository.
        
        Args:
            sieve_filter: Filter to save
            output_path: Path/location to save filter
            
        Returns:
            Path where filter was saved
            
        Raises:
            RepositoryError: If save fails
        """
        pass

    @abstractmethod
    def load(self, filter_id: str) -> SieveFilter:
        """Load filter from repository.
        
        Args:
            filter_id: ID or path of filter to load
            
        Returns:
            Loaded SieveFilter entity
            
        Raises:
            NotFoundError: If filter doesn't exist
            RepositoryError: If load fails
        """
        pass

    @abstractmethod
    def exists(self, filter_id: str) -> bool:
        """Check if filter exists in repository.
        
        Args:
            filter_id: ID or path of filter
            
        Returns:
            True if filter exists
        """
        pass

    @abstractmethod
    def list_filters(self) -> list[str]:
        """List all filters in repository.
        
        Returns:
            List of filter IDs/paths
        """
        pass

    @abstractmethod
    def delete(self, filter_id: str) -> None:
        """Delete filter from repository.
        
        Args:
            filter_id: ID or path of filter to delete
            
        Raises:
            NotFoundError: If filter doesn't exist
            RepositoryError: If delete fails
        """
        pass
