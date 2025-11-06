"""Main application for MailCow AI Filter - Hexagonal Architecture."""

import logging
import sys

from .config import Config
from .infrastructure.container import Container
from .utils import setup_logging

logger = logging.getLogger(__name__)


def main():
    """Main entry point using Hexagonal Architecture."""

    print("=" * 60)
    print("MailCow AI Filter - Email Sorting with AI-Generated Sieve Rules")
    print("=" * 60)
    print()

    # Load configuration
    try:
        config_loader = Config()
        config_dict = config_loader.config
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print()
        print("Please create config/config.yml from config/config.example.yml")
        print("or set environment variables in .env file")
        sys.exit(1)

    # Setup logging
    log_config = config_dict.get('logging', {})
    setup_logging(
        level=log_config.get('level', 'INFO'),
        log_file=log_config.get('file')
    )

    logger.info("Starting MailCow AI Filter (Hexagonal Architecture)")

    # Check protocol
    protocol = config_dict.get('protocol', 'imap').lower()
    print(f"Protocol: {protocol.upper()}")

    if protocol != 'imap':
        print()
        print("⚠️  Only IMAP is supported in this version")
        print("Please set protocol: 'imap' in config/config.yml")
        sys.exit(1)

    print()

    # Initialize container
    try:
        container = Container(config_dict)
        logger.info("Dependency injection container initialized")

        # Create use case
        analyze_use_case = container.analyze_emails_use_case()

        # Create request from configuration
        request = container.create_analyze_request()

        # Get output file path
        sieve_config = config_dict.get('sieve', {})
        output_file = sieve_config.get('output_file', '/app/output/generated.sieve')

        logger.info(f"Starting analysis: max_emails={request.max_emails}, "
                   f"exclude_folders={request.exclude_folders}")

        # Execute use case
        print("Fetching and analyzing emails...")
        print()

        response = analyze_use_case.execute(request)

        # Save the filter manually since DTO is frozen
        filter_repo = container.filter_repository()
        saved_path = filter_repo.save(response.sieve_filter, output_file)

        # Print summary
        print()
        print("=" * 60)
        print("Analysis Complete!")
        print("=" * 60)
        print()
        print(f"Analyzed: {response.total_emails_analyzed} emails")
        print(f"Identified: {response.categories_found} categories")
        print(f"Generated: {saved_path}")
        print(f"Time: {response.analysis_time_seconds:.2f}s")
        print()
        print("Next steps:")
        print(f"1. Review the generated rules in {saved_path}")
        print("2. Test with a small subset of emails")
        print("3. Upload to MailCow: Mailbox → Edit → Sieve filters")
        print()

        logger.info("MailCow AI Filter completed successfully")

    except Exception as e:
        logger.error(f"Error during analysis: {e}", exc_info=True)
        print()
        print(f"Error: {e}")
        print()
        print("Check logs for details")
        sys.exit(1)


if __name__ == '__main__':
    main()
