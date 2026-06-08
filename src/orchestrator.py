"""Orchestration functions for coordinating the processing pipeline."""

from pathlib import Path
from typing import Dict, Any, List, Tuple
from loguru import logger

from .config import ConfigLoader, ConfigValidator
from .processing.discovery import InputDiscovery
from .processing.processor import BatchProcessor
from .processing.context import ProcessorConfig
from .api.client import ReplicateClient
from .output.writer import OutputWriter
from .output.reporter import Reporter
from .utils.progress import create_progress_bar
from .utils.path_resolver import (
    resolve_input_path,
    resolve_output_base_path,
    create_timestamped_output_path,
)


def load_and_validate_config() -> Tuple[Dict[str, Any], ConfigLoader]:
    """Load and validate configuration."""
    config_loader = ConfigLoader()
    config_validator = ConfigValidator()

    config = config_loader.load_config()
    profiles = config_loader.load_profiles()
    config_validator.validate_all(config, profiles)

    return config, config_loader


def discover_inputs_and_profiles(
    config: Dict[str, Any],
) -> Tuple[List[Tuple[Path, Path]], Dict[str, Any]]:
    """Discover input files and exactly one active profile."""
    config_loader = ConfigLoader()
    profile = config_loader.load_active_profile()

    profiles_dir = Path("USER-FILES/03.PROFILES")

    input_path, project_name = resolve_input_path(config, [profile], profiles_dir)

    discovery = InputDiscovery(input_path, profiles_dir)
    prompt_files = discovery.discover_prompt_files()

    if not prompt_files:
        logger.error("No prompt files found in input directory")
        raise FileNotFoundError("No prompt files found")

    if project_name:
        logger.info(f"Project: {project_name}")

    logger.info(
        f"Found {len(prompt_files)} prompt files, using profile '{profile['profile_name']}'"
    )

    return prompt_files, profile


def initialize_services(
    args,
    config: Dict[str, Any],
    config_loader: ConfigLoader,
    api_key: str,
    profile: Dict[str, Any],
) -> Tuple[OutputWriter, Reporter, ReplicateClient, BatchProcessor]:
    """Initialize all required services."""
    output_base_path = resolve_output_base_path(config, [profile])
    output_path = create_timestamped_output_path(output_base_path)

    output_writer = OutputWriter(output_path, force_png=args.force_png)
    reporter = Reporter(output_writer)

    wrapper_config = config.get("wrapper", {})

    replicate_client = ReplicateClient(
        api_key=api_key,
        max_retries=wrapper_config.get("max_retries", 3),
        max_wait_time=wrapper_config.get("max_wait_time", 600),
        rate_limit_retry_delay=wrapper_config.get("rate_limit_retry_delay", 60),
    )

    processor_config = ProcessorConfig(
        api_client=replicate_client,
        output_writer=output_writer,
        reporter=reporter,
        save_payloads=args.save_payloads,
        dry_run=args.dry_run,
        no_progress=args.no_progress,
    )
    processor = BatchProcessor(processor_config)

    return output_writer, reporter, replicate_client, processor


def execute_processing(
    args,
    processor: BatchProcessor,
    prompt_files: List[Tuple[Path, Path]],
    profile: Dict[str, Any],
) -> bool:
    """Execute main processing logic."""
    logger.info(f"Starting batch processing with profile '{profile['profile_name']}'...")

    progress = None if args.no_progress else create_progress_bar()

    if progress:
        with progress:
            success = processor.process_all(prompt_files, profile, progress)
    else:
        success = processor.process_all(prompt_files, profile, None)

    return success


def estimate_costs(
    prompt_files: List[Tuple[Path, Path]],
    profile: Dict[str, Any],
    output_writer: OutputWriter,
) -> int:
    """Estimate processing costs without actual execution."""
    total_files = len(prompt_files)
    base_cost = profile.get("pricing", {}).get("base_cost", 0.0)
    total_cost = base_cost * total_files

    logger.info(
        f"Profile '{profile['profile_name']}': {total_files} files × ${base_cost:.3f} = ${total_cost:.2f}"
    )
    logger.info(f"\nTotal: {total_files} files")
    logger.info(f"Estimated cost: ${total_cost:.2f}")

    report_content = f"# Cost Estimation Report\n\n"
    report_content += f"- Profile: {profile['profile_name']}\n"
    report_content += f"- Total files: {total_files}\n"
    report_content += f"- Estimated total cost: ${total_cost:.2f}\n"
    output_writer.write_report(report_content, "cost_estimation.md")

    return 0


def generate_final_reports(
    processor: BatchProcessor,
    reporter: Reporter,
    prompt_files: List[Tuple[Path, Path]],
    profile: Dict[str, Any],
    success: bool,
) -> int:
    """Generate and save final processing reports."""
    summary = {
        "processed": processor.processed_count,
        "failed": processor.failed_count,
        "total_cost": processor.total_cost,
        "total_prompts": len(prompt_files),
        "profile": profile["profile_name"],
    }

    profiles_with_fixes = []
    if profile.get("prompt_prefix") or profile.get("prompt_suffix"):
        profiles_with_fixes.append({
            "profile_name": profile["profile_name"],
            "prompt_prefix": profile.get("prompt_prefix", ""),
            "prompt_suffix": profile.get("prompt_suffix", ""),
        })

    reporter.save_reports(success=success, summary=summary, profiles_with_fixes=profiles_with_fixes if profiles_with_fixes else None)

    logger.success(f"Processing complete: {summary['processed']} images generated")
    logger.info(f"Total cost: ${summary['total_cost']:.2f}")

    if success:
        logger.success("All operations completed successfully")
        return 0
    else:
        logger.error(f"Failed with {summary['failed']} errors")
        return 1
