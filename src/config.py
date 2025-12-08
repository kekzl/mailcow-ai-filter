"""Configuration loader for MailCow AI Filter."""

import os
from pathlib import Path
from typing import Any

import yaml


class ConfigurationError(Exception):
    """Raised when configuration is invalid."""

    pass


class Config:
    """Configuration loader from YAML file and environment variables."""

    # Valid AI providers
    VALID_PROVIDERS = {"ollama", "anthropic"}

    # Valid analysis modes
    VALID_ANALYSIS_MODES = {"embedding", "hierarchical", "simple"}

    def __init__(self, config_path: str | None = None) -> None:
        """Load configuration from YAML file.

        Args:
            config_path: Optional path to config file (defaults to config/config.yml)

        Raises:
            FileNotFoundError: If config file doesn't exist
            ConfigurationError: If configuration is invalid
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
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config: dict[str, Any] = yaml.safe_load(f) or {}

        # Override with environment variables if present
        self._apply_env_overrides()

        # Validate configuration
        self._validate_config()

    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides to configuration."""

        # IMAP configuration
        if os.getenv("MAIL_SERVER"):
            self.config.setdefault("imap", {})
            self.config["imap"]["server"] = os.getenv("MAIL_SERVER")

        if os.getenv("MAIL_USERNAME"):
            self.config.setdefault("imap", {})
            self.config["imap"]["username"] = os.getenv("MAIL_USERNAME")

        if os.getenv("MAIL_PASSWORD"):
            self.config.setdefault("imap", {})
            self.config["imap"]["password"] = os.getenv("MAIL_PASSWORD")

        if os.getenv("PROTOCOL"):
            self.config["protocol"] = os.getenv("PROTOCOL")

        # AI configuration
        if os.getenv("AI_PROVIDER"):
            self.config.setdefault("ai", {})
            self.config["ai"]["provider"] = os.getenv("AI_PROVIDER")

        if os.getenv("AI_MODEL"):
            self.config.setdefault("ai", {})
            self.config["ai"]["model"] = os.getenv("AI_MODEL")

        if os.getenv("OLLAMA_BASE_URL"):
            self.config.setdefault("ai", {})
            self.config["ai"]["base_url"] = os.getenv("OLLAMA_BASE_URL")

        if os.getenv("ANTHROPIC_API_KEY"):
            self.config.setdefault("ai", {})
            self.config["ai"]["api_key"] = os.getenv("ANTHROPIC_API_KEY")

        # Analysis configuration
        if os.getenv("MAX_EMAILS_TO_ANALYZE"):
            self.config.setdefault("ai", {})
            try:
                self.config["ai"]["max_emails_to_analyze"] = int(
                    os.getenv("MAX_EMAILS_TO_ANALYZE")
                )
            except (ValueError, TypeError):
                pass

        if os.getenv("ANALYSIS_MODE"):
            self.config.setdefault("ai", {})
            self.config["ai"]["analysis_mode"] = os.getenv("ANALYSIS_MODE")

        # Logging configuration
        if os.getenv("LOG_LEVEL"):
            self.config.setdefault("logging", {})
            self.config["logging"]["level"] = os.getenv("LOG_LEVEL")

    def _validate_config(self) -> None:
        """Validate configuration structure and values.

        Raises:
            ConfigurationError: If configuration is invalid
        """
        errors: list[str] = []

        # Validate IMAP configuration
        imap_config = self.config.get("imap", {})
        if not imap_config.get("server"):
            errors.append("imap.server is required")
        if not imap_config.get("username"):
            errors.append("imap.username is required")
        if not imap_config.get("password"):
            errors.append("imap.password is required")

        # Validate port if specified
        port = imap_config.get("port")
        if port is not None:
            if not isinstance(port, int) or port < 1 or port > 65535:
                errors.append(f"imap.port must be a valid port number (1-65535), got: {port}")

        # Validate AI configuration
        ai_config = self.config.get("ai", {})
        provider = ai_config.get("provider", "ollama")

        if provider not in self.VALID_PROVIDERS:
            errors.append(
                f"ai.provider must be one of {self.VALID_PROVIDERS}, got: {provider}"
            )

        # Provider-specific validation
        if provider == "anthropic":
            if not ai_config.get("api_key"):
                errors.append(
                    "ai.api_key (or ANTHROPIC_API_KEY env var) is required when using anthropic provider"
                )

        # Validate analysis mode if specified
        analysis_mode = ai_config.get("analysis_mode")
        if analysis_mode and analysis_mode not in self.VALID_ANALYSIS_MODES:
            errors.append(
                f"ai.analysis_mode must be one of {self.VALID_ANALYSIS_MODES}, got: {analysis_mode}"
            )

        # Validate max_emails_to_analyze if specified
        max_emails = ai_config.get("max_emails_to_analyze")
        if max_emails is not None:
            if not isinstance(max_emails, int) or max_emails < 1:
                errors.append(
                    f"ai.max_emails_to_analyze must be a positive integer, got: {max_emails}"
                )

        # Validate temperature if specified
        temperature = ai_config.get("temperature")
        if temperature is not None:
            if not isinstance(temperature, (int, float)) or temperature < 0 or temperature > 2:
                errors.append(
                    f"ai.temperature must be between 0 and 2, got: {temperature}"
                )

        # Raise all errors at once
        if errors:
            raise ConfigurationError(
                "Configuration validation failed:\n  - " + "\n  - ".join(errors)
            )

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            key: Configuration key (supports dot notation like 'imap.server')
            default: Default value if key doesn't exist

        Returns:
            Configuration value or default
        """
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value

    @property
    def imap(self) -> dict[str, Any]:
        """Get IMAP configuration."""
        return self.config.get("imap", {})

    @property
    def ai(self) -> dict[str, Any]:
        """Get AI configuration."""
        return self.config.get("ai", {})

    @property
    def logging_config(self) -> dict[str, Any]:
        """Get logging configuration."""
        return self.config.get("logging", {})
