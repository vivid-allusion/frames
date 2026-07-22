"""Simplified main entry point using refactored modules."""

import sys
from typing import Optional, Dict, Any
from loguru import logger

from .auth import get_api_key
from .exceptions import AuthenticationError, ConfigurationError, ValidationError
from .cli import parse_args
from .orchestrator import (
    load_and_validate_config,
    discover_inputs_and_profiles,
    initialize_services,
    execute_processing,
    estimate_costs,
    generate_final_reports,
)
from .utils.logging import setup_logging
from .processing.processor import BatchProcessor
from .output.reporter import Reporter


def setup_environment(args) -> str | None:
    """Set up logging and environment."""
    setup_logging(
        verbose=args.verbose if hasattr(args, "verbose") else False, debug=args.debug
    )
    logger.info("=" * 60)
    logger.info("Vivid Allusion Frame Composer v2.0.0")
    logger.info("=" * 60)
    return None


def authenticate_for_mode(dry_run: bool) -> str:
    """Handle authentication based on execution mode."""
    logger.info("Authenticating...")

    if dry_run:
        logger.info("Validating API key access (dry-run mode)...")
        api_key = get_api_key()
        logger.success("API key validated successfully")
    else:
        api_key = get_api_key()

    return api_key


def handle_error(
    e: Exception,
    args=None,
    reporter: Optional[Reporter] = None,
    processor: Optional[BatchProcessor] = None,
    profile: Optional[Dict[str, Any]] = None,
) -> None:
    """Handle and report errors."""
    logger.error(f"Fatal error: {e}")

    if reporter and processor and profile:
        try:
            summary = {
                "processed": processor.processed_count,
                "failed": processor.failed_count,
                "total_cost": processor.total_cost,
            }
            reporter.save_reports(success=False, summary=summary, error_message=str(e))
        except Exception as report_error:
            logger.error(f"Could not save error report: {report_error}")


def main():
    """Main execution function."""
    args = parse_args()

    # Initialize environment
    setup_environment(args)

    # Initialize variables for error handling
    reporter = None
    processor = None
    profile = None

    try:
        # Load configuration
        config, _ = load_and_validate_config()

        # Authenticate with Replicate
        api_key = authenticate_for_mode(args.dry_run)

        # Discover inputs and profiles
        prompt_files, profile = discover_inputs_and_profiles(config)

        # Initialize services
        output_writer, reporter, replicate_client, processor = initialize_services(
            args, config, api_key, profile
        )

        # Handle cost estimation mode
        if args.cost_estimation:
            return estimate_costs(prompt_files, profile, output_writer)

        # Execute main processing
        success = execute_processing(args, processor, prompt_files, profile)

        # Generate final reports
        return generate_final_reports(
            processor, reporter, prompt_files, profile, success
        )

    except KeyboardInterrupt:
        logger.warning("Interrupted by user")
        return 130
    except (AuthenticationError, ConfigurationError, ValidationError) as e:
        # These are expected fail-fast errors - don't need full error handling
        logger.error(f"Error: {e}")
        return 1
    except Exception as e:
        handle_error(e, args, reporter, processor, profile)
        return 1


if __name__ == "__main__":
    sys.exit(main())
