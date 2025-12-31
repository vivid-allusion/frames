"""Orchestration functions for coordinating the processing pipeline."""
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from loguru import logger

from .config import ConfigLoader, ConfigValidator
from .processing.discovery import InputDiscovery
from .processing.processor import MatrixProcessor
from .processing.context import ProcessorConfig
from .api.client import ReplicateClient
from .output.writer import OutputWriter
from .output.reporter import Reporter
from .utils.progress import create_progress_bar
from .constants import TIMESTAMP_FORMAT
from datetime import datetime


def load_and_validate_config() -> Tuple[Dict[str, Any], ConfigLoader]:
    """Load and validate configuration."""
    config_loader = ConfigLoader()
    config_validator = ConfigValidator()

    config = config_loader.load_config()
    config_validator.validate(config)

    return config, config_loader


def discover_inputs_and_profiles(config: Dict[str, Any]) -> Tuple[List[Tuple[Path, Path]], List[Dict[str, Any]]]:
    """Discover input files and active profiles."""
    # Discover inputs
    input_dir = Path(config['inputs']['directory'])
    output_dir = Path(config['outputs']['directory'])
    discovery = InputDiscovery(input_dir, output_dir)
    prompt_files = discovery.discover_prompt_files()

    if not prompt_files:
        logger.error("No prompt files found in input directory")
        raise FileNotFoundError("No prompt files found")

    # Load active profiles
    config_loader = ConfigLoader()
    active_models = config_loader.load_active_profiles()

    logger.info(f"Found {len(prompt_files)} prompt files and {len(active_models)} active profiles")

    return prompt_files, active_models


def initialize_services(
    args,
    config: Dict[str, Any],
    config_loader: ConfigLoader,
    api_key: str
) -> Tuple[OutputWriter, Reporter, ReplicateClient, MatrixProcessor]:
    """Initialize all required services."""
    # Create timestamped output directory
    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    output_base_path = Path(config['outputs']['directory'])
    output_path = output_base_path / f"{timestamp}_IMAGE"
    output_path.mkdir(parents=True, exist_ok=True)

    # Initialize services
    output_writer = OutputWriter(output_path, force_png=args.force_png)
    reporter = Reporter(output_writer)

    # Initialize API client
    wrapper_config = config.get('wrapper', {})
    queue_config = wrapper_config.get('queue', {})

    replicate_client = ReplicateClient(
        api_key=api_key,
        max_retries=wrapper_config.get('max_retries', 3),
        polling_interval=queue_config.get('polling_interval', 0.5),
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


def execute_processing(args, processor: MatrixProcessor, prompt_files: List[Tuple[Path, Path]], active_models: List[Dict[str, Any]]) -> bool:
    """Execute main processing logic."""
    logger.info("Starting matrix processing...")

    # Create progress bar if not disabled
    progress = None if args.no_progress else create_progress_bar()

    if progress:
        with progress:
            success = processor.process_all(prompt_files, active_models, progress)
    else:
        success = processor.process_all(prompt_files, active_models, None)

    return success


def estimate_costs(prompt_files: List[Tuple[Path, Path]], active_models: List[Dict[str, Any]], output_writer: OutputWriter) -> int:
    """Estimate processing costs without actual execution."""
    total_combinations = len(prompt_files) * len(active_models)
    total_cost = 0.0

    for model in active_models:
        base_cost = model.get('pricing', {}).get('base_cost', 0.0)
        combinations_per_model = len(prompt_files)
        model_cost = base_cost * combinations_per_model
        total_cost += model_cost

        logger.info(f"Profile '{model['profile_name']}': {combinations_per_model} files × ${base_cost:.3f} = ${model_cost:.2f}")

    logger.info(f"\nTotal: {total_combinations} combinations")
    logger.info(f"Estimated cost: ${total_cost:.2f}")

    # Save estimation report
    report_content = f"# Cost Estimation Report\n\n"
    report_content += f"- Total combinations: {total_combinations}\n"
    report_content += f"- Estimated total cost: ${total_cost:.2f}\n"
    output_writer.save_report(report_content, "cost_estimation")

    return 0


def generate_final_reports(
    processor: MatrixProcessor,
    reporter: Reporter,
    prompt_files: List[Tuple[Path, Path]],
    active_models: List[Dict[str, Any]],
    success: bool
) -> int:
    """Generate and save final processing reports."""
    # Generate summary report
    summary = reporter.generate_summary(
        processed=processor.processed_count,
        failed=processor.failed_count,
        total_cost=processor.total_cost
    )

    # Generate full report
    report_content = reporter.generate_report(
        prompt_files=prompt_files,
        models=active_models,
        processed=processor.processed_count,
        failed=processor.failed_count,
        total_cost=processor.total_cost
    )

    # Save reports
    processor.output_writer.save_report(report_content, "processing_report")

    # Display summary
    logger.success(f"✅ Processing complete: {summary['processed']} images generated")
    logger.info(f"💰 Total cost: ${summary['total_cost']:.2f}")

    if success:
        logger.success("✅ All operations completed successfully")
        return 0
    else:
        logger.error(f"❌ Failed with {summary['failed']} errors")
        return 1