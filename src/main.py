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
from .processing.processor import MatrixProcessor
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


def discover_inputs_and_profiles(config: Dict[str, Any]) -> Tuple[List[Tuple[Path, Path]], List[Dict[str, Any]]]:
    """Discover input files and profile configurations."""
    logger.info("Discovering inputs...")
    discovery = InputDiscovery(
        input_dir=Path("USER-FILES/04.INPUT"),
        profiles_dir=Path("USER-FILES/03.PROFILES")
    )
    
    prompt_files = discovery.discover_prompt_files()
    profiles = discovery.discover_profiles()
    active_models = discovery.get_active_models(profiles)
    
    # Validate configuration
    validator = ConfigValidator()
    validator.validate_all(config, profiles)
    
    return prompt_files, active_models


def build_profiles_with_fixes(active_models: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Build list of profiles that have prompt fixes."""
    profiles_with_fixes = []
    for model_info in active_models:
        if model_info.get('prompt_prefix') or model_info.get('prompt_suffix'):
            profiles_with_fixes.append({
                'profile_name': model_info['profile_name'],
                'prompt_prefix': model_info.get('prompt_prefix', ''),
                'prompt_suffix': model_info.get('prompt_suffix', '')
            })
    return profiles_with_fixes


def estimate_costs(
    prompt_files: List[Tuple[Path, Path]], 
    active_models: List[Dict[str, Any]],
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
    total_images = total_prompts * len(active_models)
    total_cost = 0.0
    
    for model_info in active_models:
        cost = model_info.get('pricing', {}).get('base_cost', 0.0)
        total_cost += cost * total_prompts
    
    estimation = f"""# Cost Estimation

## Summary
- **Prompt Files**: {len(prompt_files)}
- **Active Profiles**: {len(active_models)}
- **Total Prompts**: {total_prompts}
- **Total Images**: {total_images}
- **Estimated Cost**: ${total_cost:.4f}

## Profiles
"""
    for model_info in active_models:
        cost = model_info.get('pricing', {}).get('base_cost', 0.0)
        profile_name = model_info['profile_name']
        description = model_info.get('description', '')
        estimation += f"- **{profile_name}**: ${cost:.4f} per image"
        if description:
            estimation += f" - {description}"
        estimation += "\n"
    
    output_writer.write_report(estimation, "COST-ESTIMATION.md")
    logger.info(f"Cost estimation saved. Total: ${total_cost:.4f}")
    return 0


def initialize_services(
    args,
    config: Dict[str, Any],
    config_loader: ConfigLoader,
    api_key: str
) -> Tuple[OutputWriter, Reporter, ReplicateClient, MatrixProcessor]:
    """Initialize all required services."""
    # Initialize output structure
    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    output_dir = Path("USER-FILES/05.OUTPUT") / f"{timestamp}_IMAGE"
    
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
    processor = MatrixProcessor(processor_config)
    
    return output_writer, reporter, replicate_client, processor


def execute_processing(
    args,
    processor: MatrixProcessor,
    prompt_files: List[Tuple[Path, Path]],
    active_models: List[Dict[str, Any]]
) -> bool:
    """Execute main processing logic."""
    logger.info("Starting matrix processing...")
    
    # Create progress bar if not disabled
    progress = None if args.no_progress else create_progress_bar()
    
    if progress:
        with progress:
            success = processor.process_all(
                prompt_files, active_models, progress
            )
    else:
        success = processor.process_all(
            prompt_files, active_models, None
        )
    
    return success


def generate_final_reports(
    processor: MatrixProcessor,
    reporter: Reporter,
    prompt_files: List[Tuple[Path, Path]],
    active_models: List[Dict[str, Any]],
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
    summary['total_models'] = len(active_models)
    
    # Collect profiles with prompt fixes
    profiles_with_fixes = build_profiles_with_fixes(active_models)
    
    reporter.save_reports(success, summary, profiles_with_fixes=profiles_with_fixes)
    
    if success:
        logger.success(f"✅ Completed successfully! Generated {summary['processed']} images")
        return 0
    else:
        logger.error(f"❌ Failed with {summary['failed']} errors")
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
    processor: Optional[MatrixProcessor] = None,
    active_models: Optional[List[Dict[str, Any]]] = None
) -> None:
    """Handle and report errors."""
    logger.error(f"Fatal error: {e}")
    
    # Try to save failure report
    try:
        if reporter and processor:
            summary = processor.get_summary() if processor else {}
            # Try to collect profiles with fixes if available
            profiles_with_fixes = build_profiles_with_fixes(active_models) if active_models else []
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