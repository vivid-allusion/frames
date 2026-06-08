"""Main entry point for Replicate wrapper."""
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
from loguru import logger

from .auth.onepassword import ensure_op_auth, get_api_key
from .config import ConfigLoader, ConfigValidator
from .exceptions import AuthenticationError, ConfigurationError, ValidationError
from .processing.discovery import InputDiscovery
from .processing.processor import BatchProcessor
from .processing.context import ProcessorConfig
from .api.client import ReplicateClient
from .output.writer import OutputWriter
from .output.reporter import Reporter
from .utils.logging import setup_logging
from .utils.progress import create_progress_bar
from .constants import TIMESTAMP_FORMAT


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Replicate Image Generation Wrapper"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Test without making API calls"
    )
    
    parser.add_argument(
        "--cost-estimation",
        action="store_true",
        help="Calculate costs without generating images"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with detailed logging"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable progress bar"
    )
    
    parser.add_argument(
        "--no-save-payloads",
        action="store_false",
        dest="save_payloads",
        default=True,
        help="Disable saving JSON payload files for each generated image"
    )
    
    parser.add_argument(
        "--force-png",
        action="store_true",
        help="Convert all images to PNG format"
    )
    
    return parser.parse_args()


def setup_environment(args) -> None:
    """Set up logging and environment."""
    setup_logging(verbose=args.verbose, debug=args.debug)
    logger.info("Environment initialized")


def load_and_validate_config() -> Tuple[Dict[str, Any], ConfigLoader]:
    """Load and validate configuration."""
    logger.info("Loading configuration...")
    config_loader = ConfigLoader()
    config = config_loader.load_config()
    return config, config_loader


def discover_inputs_and_profiles(config: Dict[str, Any]) -> Tuple[List[Tuple[Path, Path]], Dict[str, Any]]:
    """Discover input files and exactly one active profile."""
    logger.info("Discovering inputs...")
    discovery = InputDiscovery(
        input_dir=Path("USER-FILES/04.INPUT"),
        profiles_dir=Path("USER-FILES/03.PROFILES")
    )
    
    prompt_files = discovery.discover_prompt_files()
    profiles = discovery.discover_profiles()
    active_models = discovery.get_active_models(profiles)
    
    if len(active_models) == 0:
        logger.error("No valid profiles found")
        sys.exit(1)
    if len(active_models) > 1:
        logger.error(f"Multiple profiles found ({len(active_models)}). Keep only ONE.")
        sys.exit(1)
    
    # Validate configuration
    validator = ConfigValidator()
    validator.validate_all(config, profiles)
    
    logger.info(f"Using profile: {active_models[0]['profile_name']}")
    return prompt_files, active_models[0]


def build_profiles_with_fixes(profile: Dict[str, Any]) -> List[Dict[str, str]]:
    """Build list of profiles that have prompt fixes."""
    profiles_with_fixes = []
    if profile.get('prompt_prefix') or profile.get('prompt_suffix'):
        profiles_with_fixes.append({
            'profile_name': profile['profile_name'],
            'prompt_prefix': profile.get('prompt_prefix', ''),
            'prompt_suffix': profile.get('prompt_suffix', '')
        })
    return profiles_with_fixes


def estimate_costs(
    prompt_files: List[Tuple[Path, Path]], 
    profile: Dict[str, Any],
    output_writer: OutputWriter
) -> int:
    """Calculate and save cost estimation."""
    discovery = InputDiscovery(
        input_dir=Path("USER-FILES/04.INPUT"),
        profiles_dir=Path("USER-FILES/03.PROFILES")
    )
    
    total_prompts = sum(
        len(discovery.load_prompts(f[0])) for f in prompt_files
    )
    total_cost = profile.get('pricing', {}).get('base_cost', 0.0) * total_prompts
    profile_name = profile['profile_name']
    
    estimation = f"""# Cost Estimation

## Summary
- **Prompt Files**: {len(prompt_files)}
- **Profile**: {profile_name}
- **Total Prompts**: {total_prompts}
- **Estimated Cost**: ${total_cost:.4f}

## Profile
- **{profile_name}**: ${profile.get('pricing', {}).get('base_cost', 0.0):.4f} per image"""
    if profile.get('description'):
        estimation += f" - {profile['description']}"
    estimation += "\n"
    
    output_writer.write_report(estimation, "COST-ESTIMATION.md")
    logger.info(f"Cost estimation saved. Total: ${total_cost:.4f}")
    return 0


def initialize_services(
    args,
    config: Dict[str, Any],
    config_loader: ConfigLoader,
    api_key: str
) -> Tuple[OutputWriter, Reporter, ReplicateClient, BatchProcessor]:
    """Initialize all required services."""
    # Initialize output structure
    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    output_dir = Path("USER-FILES/05.OUTPUT") / f"{timestamp}_IMG-TO-IMG"
    
    # Get force_png setting (CLI flag overrides config)
    output_config = config.get('output', {})
    force_png = args.force_png or output_config.get('force_png', False)
    
    output_writer = OutputWriter(output_dir, force_png=force_png)
    reporter = Reporter(output_writer)
    
    logger.info(f"Output directory: {output_dir}")
    
    # Initialize Replicate client
    wrapper_config = config_loader.get_wrapper_config()
    queue_config = config_loader.get_queue_config()
    
    replicate_client = ReplicateClient(
        api_key=api_key,
        timeout=wrapper_config.get('timeout', 120),
        max_retries=wrapper_config.get('max_retries', 3),
        max_wait_time=wrapper_config.get('max_wait_time', 600),
        rate_limit_retry_delay=queue_config.get('rate_limit_retry_delay', 60)
    )
    
    # Initialize processor
    processor_config = ProcessorConfig(
        api_client=replicate_client,
        output_writer=output_writer,
        reporter=reporter,
        save_payloads=args.save_payloads,
        dry_run=args.dry_run,
        no_progress=args.no_progress
    )
    processor = BatchProcessor(processor_config)
    
    return output_writer, reporter, replicate_client, processor


def execute_processing(
    args,
    processor: BatchProcessor,
    prompt_files: List[Tuple[Path, Path]],
    profile: Dict[str, Any]
) -> bool:
    """Execute main processing logic."""
    logger.info(f"Starting batch processing with profile '{profile['profile_name']}'...")
    
    progress = None if args.no_progress else create_progress_bar()
    
    if progress:
        with progress:
            success = processor.process_all(
                prompt_files, profile, progress
            )
    else:
        success = processor.process_all(
            prompt_files, profile, None
        )
    
    return success


def generate_final_reports(
    processor: BatchProcessor,
    reporter: Reporter,
    prompt_files: List[Tuple[Path, Path]],
    profile: Dict[str, Any],
    success: bool
) -> int:
    """Generate and save final reports."""
    discovery = InputDiscovery(
        input_dir=Path("USER-FILES/04.INPUT"),
        profiles_dir=Path("USER-FILES/03.PROFILES")
    )
    
    summary = processor.get_summary()
    summary['total_prompts'] = sum(
        len(discovery.load_prompts(f[0])) for f in prompt_files
    )
    summary['profile'] = profile['profile_name']
    
    profiles_with_fixes = build_profiles_with_fixes(profile)
    
    reporter.save_reports(success, summary, profiles_with_fixes=profiles_with_fixes)
    
    if success:
        logger.success(f"Completed successfully! Generated {summary['processed']} images")
        return 0
    else:
        logger.error(f"Failed with {summary['failed']} errors")
        return 1


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
    args,
    reporter: Optional[Reporter] = None,
    processor: Optional[BatchProcessor] = None,
    profile: Optional[Dict[str, Any]] = None
) -> None:
    """Handle and report errors."""
    logger.error(f"Fatal error: {e}")
    
    try:
        if reporter and processor:
            summary = processor.get_summary() if processor else {}
            profiles_with_fixes = build_profiles_with_fixes(profile) if profile else []
            reporter.save_reports(False, summary, str(e), profiles_with_fixes=profiles_with_fixes)
    except Exception:
        pass
    
    if args.debug:
        logger.exception("Full traceback:")


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
        config, config_loader = load_and_validate_config()

        # Authenticate with 1Password
        api_key = authenticate_for_mode(args.dry_run)
        
        # Discover inputs and profiles
        prompt_files, profile = discover_inputs_and_profiles(config)
        
        # Initialize services
        output_writer, reporter, replicate_client, processor = initialize_services(
            args, config, config_loader, api_key
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
        logger.error(f"Error: {e}")
        return 1
    except Exception as e:
        handle_error(e, args, reporter, processor, profile)
        return 1


if __name__ == "__main__":
    sys.exit(main())