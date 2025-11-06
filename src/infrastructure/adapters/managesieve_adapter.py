"""ManageSieve Adapter - Fetch existing Sieve filters."""

from __future__ import annotations

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class ManageSieveAdapter:
    """Adapter for fetching Sieve filters via ManageSieve protocol."""

    def __init__(
        self,
        server: str,
        username: str,
        password: str,
        port: int = 4190,
    ) -> None:
        """Initialize ManageSieve adapter.

        Args:
            server: ManageSieve server hostname (usually same as IMAP)
            username: Email address
            password: Password
            port: ManageSieve port (default: 4190)
        """
        self.server = server
        self.username = username
        self.password = password
        self.port = port
        self.connection = None

        logger.info(f"Initialized ManageSieve adapter for {server}:{port}")

    def connect(self) -> None:
        """Connect to ManageSieve server.

        Raises:
            ConnectionError: If connection fails
        """
        try:
            # Try importing managesieve library
            try:
                from managesieve import MANAGESIEVE
            except ImportError:
                logger.warning(
                    "managesieve library not installed. "
                    "Falling back to IMAP GETMETADATA for filter detection."
                )
                raise ImportError("managesieve not available")

            self.connection = MANAGESIEVE(self.server, self.port)
            self.connection.login(self.username, self.password)
            logger.info(f"Connected to ManageSieve server {self.server}")

        except ImportError:
            # Library not available - we'll use a different approach
            raise
        except Exception as e:
            logger.error(f"Failed to connect to ManageSieve server: {e}")
            raise ConnectionError(f"ManageSieve connection failed: {e}") from e

    def disconnect(self) -> None:
        """Disconnect from ManageSieve server."""
        if self.connection:
            try:
                self.connection.logout()
                logger.info("Disconnected from ManageSieve server")
            except Exception as e:
                logger.warning(f"Error during disconnect: {e}")
            finally:
                self.connection = None

    def list_scripts(self) -> List[str]:
        """List all Sieve scripts.

        Returns:
            List of script names
        """
        if not self.connection:
            raise ConnectionError("Not connected. Call connect() first.")

        try:
            scripts = self.connection.listscripts()
            logger.info(f"Found {len(scripts)} Sieve scripts")
            return [script[0] for script in scripts]
        except Exception as e:
            logger.error(f"Error listing scripts: {e}")
            return []

    def get_script(self, script_name: str) -> str:
        """Fetch a Sieve script by name.

        Args:
            script_name: Name of the script

        Returns:
            Script content
        """
        if not self.connection:
            raise ConnectionError("Not connected. Call connect() first.")

        try:
            script_content = self.connection.getscript(script_name)
            logger.info(f"Fetched script: {script_name}")
            return script_content
        except Exception as e:
            logger.error(f"Error fetching script {script_name}: {e}")
            return ""

    def get_active_script(self) -> str | None:
        """Get the currently active Sieve script.

        Returns:
            Active script content or None
        """
        if not self.connection:
            raise ConnectionError("Not connected. Call connect() first.")

        try:
            scripts = self.connection.listscripts()
            # Find the active script (marked with *)
            for script_name, active in scripts:
                if active:
                    return self.get_script(script_name)
            return None
        except Exception as e:
            logger.error(f"Error getting active script: {e}")
            return None

    def get_all_scripts(self) -> Dict[str, str]:
        """Get all Sieve scripts with their content.

        Returns:
            Dictionary mapping script names to content
        """
        if not self.connection:
            raise ConnectionError("Not connected. Call connect() first.")

        scripts = {}
        try:
            script_names = self.list_scripts()
            for name in script_names:
                content = self.get_script(name)
                if content:
                    scripts[name] = content
            logger.info(f"Retrieved {len(scripts)} scripts")
            return scripts
        except Exception as e:
            logger.error(f"Error getting all scripts: {e}")
            return {}


class SieveFilterExtractor:
    """Extract existing filters from Sieve scripts for AI analysis."""

    @staticmethod
    def extract_existing_filters(script_content: str) -> List[Dict[str, str]]:
        """Parse Sieve script and extract filter rules.

        Args:
            script_content: Sieve script content

        Returns:
            List of filter rules with descriptions
        """
        filters = []

        if not script_content:
            return filters

        lines = script_content.split("\n")
        current_rule = None
        current_description = ""

        for line in lines:
            line = line.strip()

            # Extract comments as descriptions
            if line.startswith("#"):
                comment = line[1:].strip()
                if comment and not comment.startswith("="):
                    # Skip separator lines
                    if current_description:
                        current_description += " " + comment
                    else:
                        current_description = comment

            # Detect rule start (if anyof/allof)
            elif "if " in line.lower():
                if current_rule:
                    filters.append(current_rule)
                current_rule = {"description": current_description, "rule": line}
                current_description = ""

            # Continuation of rule
            elif current_rule and line:
                current_rule["rule"] += " " + line

            # Rule end
            elif current_rule and "}" in line:
                current_rule["rule"] += " " + line
                filters.append(current_rule)
                current_rule = None

        # Add last rule if exists
        if current_rule:
            filters.append(current_rule)

        logger.info(f"Extracted {len(filters)} existing filter rules")
        return filters

    @staticmethod
    def summarize_existing_filters(filters: List[Dict[str, str]]) -> str:
        """Create a summary of existing filters for AI analysis.

        Args:
            filters: List of existing filter rules

        Returns:
            Human-readable summary
        """
        if not filters:
            return "No existing filters found."

        summary = f"Found {len(filters)} existing Sieve filter rules:\n\n"

        for i, filter_rule in enumerate(filters, 1):
            desc = filter_rule.get("description", "No description")
            rule = filter_rule.get("rule", "")

            # Try to extract folder destination
            folder = "unknown"
            if "fileinto" in rule:
                import re

                match = re.search(r'fileinto\s+"([^"]+)"', rule)
                if match:
                    folder = match.group(1)

            summary += f"{i}. {desc}\n"
            summary += f"   → Moves to: {folder}\n"
            summary += f"   Rule: {rule[:100]}...\n\n"

        return summary
