"""Simplified main entry point using refactored modules."""
import sys
from typing import Optional, List, Dict, Any
from loguru import logger

from .auth.onepassword import ensure_op_auth, get_api_key
from .exceptions import AuthenticationError, ConfigurationError, ValidationError
from .cli import parse_args
from .orchestrator import (
    load_and_validate_config,
    discover_inputs_and_profiles,
    initialize_services,
    execute_processing,
    estimate_costs,
    generate_final_reports
)
from .utils.logging import setup_logging
from .processing.processor import MatrixProcessor
from .output.reporter import Reporter


def setup_environment(args) -> None:
    """Set up logging and environment."""
    setup_logging(verbose=args.verbose if hasattr(args, 'verbose') else False, debug=args.debug)
    logger.info("Environment initialized")


def authenticate_for_mode(dry_run: bool) -> str:
    """Handle authentication based on execution mode."""
    logger.info("Authenticating with 1Password...")
    ensure_op_auth()

    if dry_run:
        logger.info("Validating API key access (dry-run mode)...")
        api_key = get_api_key()
        logger.success("✅ API key validated successfully")
    else:
        api_key = get_api_key()

    return api_key


def handle_error(
    e: Exception,
    args=None,
    reporter: Optional[Reporter] = None,
    processor: Optional[MatrixProcessor] = None,
    active_models: Optional[List[Dict[str, Any]]] = None
) -> None:
    """Handle and report errors."""
    logger.error(f"Fatal error: {e}")

    # Try to save failure report
    if reporter and processor and active_models:
        try:
            report = reporter.generate_failure_report(
                error=str(e),
                processed=processor.processed_count,
                failed=processor.failed_count
            )
            processor.output_writer.save_report(report, "error_report")
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
    active_models = None

    try:
        # Load configuration
        config, config_loader = load_and_validate_config()

        # Authenticate with 1Password
        api_key = authenticate_for_mode(args.dry_run)

        # Discover inputs and profiles
        prompt_files, active_models = discover_inputs_and_profiles(config)

        # Initialize services
        output_writer, reporter, replicate_client, processor = initialize_services(
            args, config, config_loader, api_key
        )

        # Handle cost estimation mode
        if args.cost_estimation:
            return estimate_costs(prompt_files, active_models, output_writer)

        # Execute main processing
        success = execute_processing(args, processor, prompt_files, active_models)

        # Generate final reports
        return generate_final_reports(
            processor, reporter, prompt_files, active_models, success
        )

    except KeyboardInterrupt:
        logger.warning("Interrupted by user")
        return 130
    except (AuthenticationError, ConfigurationError, ValidationError) as e:
        # These are expected fail-fast errors - don't need full error handling
        logger.error(f"Error: {e}")
        return 1
    except Exception as e:
        handle_error(e, args, reporter, processor, active_models)
        return 1


if __name__ == "__main__":
    sys.exit(main())