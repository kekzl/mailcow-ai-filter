"""Sieve File Adapter - Implements IFilterRepository port."""

from __future__ import annotations

import logging
from pathlib import Path

from src.application.ports.i_filter_repository import IFilterRepository
from src.domain.entities.sieve_filter import SieveFilter

logger = logging.getLogger(__name__)


class SieveFileAdapter(IFilterRepository):
    """Sieve file adapter for filter persistence."""

    def __init__(self, default_output_dir: str = "/app/output") -> None:
        """Initialize Sieve file adapter.

        Args:
            default_output_dir: Default directory for saving filters
        """
        self.default_output_dir = default_output_dir
        logger.info(
            f"Initialized Sieve file adapter (output_dir: {default_output_dir})"
        )

    def save(self, sieve_filter: SieveFilter, output_path: str) -> str:
        """Save filter to Sieve file.

        Args:
            sieve_filter: Filter to save
            output_path: Path where filter should be saved

        Returns:
            Path where filter was saved

        Raises:
            Exception: If save fails
        """
        try:
            # Ensure directory exists
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Generate Sieve script
            sieve_script = sieve_filter.to_sieve_script()

            # Write to file
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(sieve_script)

            logger.info(f"Saved Sieve filter to {output_file}")
            logger.info(f"Generated {len(sieve_filter.rules)} rules")

            return str(output_file)

        except Exception as e:
            logger.error(f"Failed to save Sieve filter: {e}")
            raise

    def load(self, filter_id: str) -> SieveFilter:
        """Load filter from Sieve file.

        Args:
            filter_id: Path to Sieve file

        Returns:
            Loaded SieveFilter entity

        Raises:
            NotImplementedError: Loading from Sieve files not yet implemented
        """
        raise NotImplementedError("Loading from Sieve files not yet implemented")

    def exists(self, filter_id: str) -> bool:
        """Check if filter file exists.

        Args:
            filter_id: Path to filter file

        Returns:
            True if file exists
        """
        return Path(filter_id).exists()

    def list_filters(self) -> list[str]:
        """List all Sieve filter files.

        Returns:
            List of filter file paths
        """
        try:
            output_dir = Path(self.default_output_dir)
            if not output_dir.exists():
                return []

            sieve_files = list(output_dir.glob("*.sieve"))
            return [str(f) for f in sieve_files]

        except Exception as e:
            logger.error(f"Error listing filters: {e}")
            return []

    def delete(self, filter_id: str) -> None:
        """Delete filter file.

        Args:
            filter_id: Path to filter file

        Raises:
            FileNotFoundError: If file doesn't exist
            Exception: If delete fails
        """
        try:
            filter_path = Path(filter_id)
            if not filter_path.exists():
                raise FileNotFoundError(f"Filter file not found: {filter_id}")

            filter_path.unlink()
            logger.info(f"Deleted filter file: {filter_id}")

        except Exception as e:
            logger.error(f"Failed to delete filter: {e}")
            raise
