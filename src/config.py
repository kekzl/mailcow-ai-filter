"""Configuration loader for MailCow AI Filter."""

import os
from pathlib import Path
from typing import Any

import yaml


class Config:
    """Configuration loader from YAML file and environment variables."""

    def __init__(self, config_path: str | None = None) -> None:
        """Load configuration from YAML file.

        Args:
            config_path: Optional path to config file (defaults to config/config.yml)

        Raises:
            FileNotFoundError: If config file doesn't exist
        """
        if config_path is None:
            # Default to config/config.yml relative to project root
            project_root = Path(__file__).parent.parent
            config_path = project_root / "config" / "config.yml"

        self.config_path = Path(config_path)

        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Config file not found: {self.config_path}\n"
                "Please create config/config.yml from config/config.example.yml"
            )

        # Load YAML configuration
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config: dict[str, Any] = yaml.safe_load(f) or {}

        # Override with environment variables if present
        self._apply_env_overrides()

    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides to configuration."""

        # IMAP configuration
        if os.getenv('MAIL_SERVER'):
            self.config.setdefault('imap', {})
            self.config['imap']['server'] = os.getenv('MAIL_SERVER')

        if os.getenv('MAIL_USERNAME'):
            self.config.setdefault('imap', {})
            self.config['imap']['username'] = os.getenv('MAIL_USERNAME')

        if os.getenv('MAIL_PASSWORD'):
            self.config.setdefault('imap', {})
            self.config['imap']['password'] = os.getenv('MAIL_PASSWORD')

        if os.getenv('PROTOCOL'):
            self.config['protocol'] = os.getenv('PROTOCOL')

        # AI configuration
        if os.getenv('AI_PROVIDER'):
            self.config.setdefault('ai', {})
            self.config['ai']['provider'] = os.getenv('AI_PROVIDER')

        if os.getenv('AI_MODEL'):
            self.config.setdefault('ai', {})
            self.config['ai']['model'] = os.getenv('AI_MODEL')

        if os.getenv('OLLAMA_BASE_URL'):
            self.config.setdefault('ai', {})
            self.config['ai']['base_url'] = os.getenv('OLLAMA_BASE_URL')

        # Analysis configuration
        if os.getenv('MAX_EMAILS_TO_ANALYZE'):
            self.config.setdefault('ai', {})
            try:
                self.config['ai']['max_emails_to_analyze'] = int(os.getenv('MAX_EMAILS_TO_ANALYZE'))
            except (ValueError, TypeError):
                pass

        # Logging configuration
        if os.getenv('LOG_LEVEL'):
            self.config.setdefault('logging', {})
            self.config['logging']['level'] = os.getenv('LOG_LEVEL')
