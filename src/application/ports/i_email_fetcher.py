"""IEmailFetcher port - Interface for fetching emails."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Sequence

from src.domain.entities.email import Email


class IEmailFetcher(ABC):
    """Port interface for email fetching adapters.
    
    Implementations might include:
    - IMAPAdapter
    - ActiveSyncAdapter
    - MockEmailAdapter (for testing)
    """

    @abstractmethod
    def connect(self) -> None:
        """Establish connection to email server.
        
        Raises:
            ConnectionError: If connection fails
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close connection to email server."""
        pass

    @abstractmethod
    def fetch_emails(
        self,
        folder: str = "INBOX",
        since_date: datetime | None = None,
        max_emails: int | None = None,
        exclude_folders: list[str] | None = None,
    ) -> Sequence[Email]:
        """Fetch emails from server.
        
        Args:
            folder: Folder to fetch from (default: INBOX)
            since_date: Only fetch emails after this date
            max_emails: Maximum number of emails to fetch
            exclude_folders: Folders to exclude from fetching
            
        Returns:
            Sequence of Email entities
            
        Raises:
            ConnectionError: If not connected
            FetchError: If fetching fails
        """
        pass

    @abstractmethod
    def list_folders(self) -> list[str]:
        """List all available folders.
        
        Returns:
            List of folder names
        """
        pass

    @abstractmethod
    def get_folder_count(self, folder: str) -> int:
        """Get email count for a folder.
        
        Args:
            folder: Folder name
            
        Returns:
            Number of emails in folder
        """
        pass
