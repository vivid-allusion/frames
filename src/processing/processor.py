"""Single-profile batch processing loop."""

from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import time
from loguru import logger

# Progress handling moved to utils.progress
from ..api.client import ReplicateClient
from ..output.writer import OutputWriter
from ..output.reporter import Reporter
from .discovery import InputDiscovery
from .context import (
    ProcessingContext,
    CombinationProcessingContext,
    ProcessorConfig,
)
from .validator import GenericValidator
from ..exceptions import ValidationError
from .markdown_parser import extract_all_image_urls


class BatchProcessor:
    """Process all input files against a single profile."""

    def __init__(self, config: ProcessorConfig):
        """
        Initialize batch processor with configuration.

        Args:
            config: ProcessorConfig containing all initialization parameters
        """
        self.replicate_client = config.api_client
        self.output_writer = config.output_writer
        self.reporter = config.reporter
        self.dry_run = config.dry_run
        self.debug = False  # Not in config, always False
        self.save_payloads = config.save_payloads
        self.total_cost = 0.0
        self.processed_count = 0
        self.failed_count = 0
        self.validator = GenericValidator()

    def process_all(
        self,
        prompt_files: List[Tuple[Path, Path]],
        profile: Dict[str, Any],
        progress: Optional[Any] = None,
    ) -> bool:
        """
        Process all input files against a single profile.

        Args:
            prompt_files: List of tuples (absolute_path, relative_path)
            profile: Single profile dictionary
            progress: Optional rich Progress bar

        Returns:
            True if all successful, False if any failures
        """
        total_files = len(prompt_files)
        logger.info(
            f"Processing {total_files} files with profile '{profile['profile_name']}'"
        )

        task_id = self._init_progress(progress, total_files)

        success = True
        for i, prompt_file_tuple in enumerate(prompt_files):
            combo_ctx = CombinationProcessingContext(
                model_info=profile,
                prompt_file_tuple=prompt_file_tuple,
                output_dir=self.output_writer.output_dir,
                combination_num=i + 1,
                total_combinations=total_files,
                progress=progress,
                task_id=task_id,
            )
            success = self._process_single_combination(combo_ctx, success)

        return success

    def _init_progress(self, progress: Optional[Any], total: int) -> Optional[int]:
        """Initialize progress bar if available."""
        if progress:
            return progress.add_task("Processing batch", total=total)
        return None

    def _process_single_combination(
        self, ctx: CombinationProcessingContext, success: bool
    ) -> bool:
        """Process a single file-model combination using context."""
        prompt_file, relative_path = ctx.prompt_file_tuple
        profile_name = ctx.model_info["profile_name"]

        # Read markdown file content
        with open(prompt_file, "r", encoding="utf-8") as f:
            markdown_content = f.read()

        # Extract all image URLs from markdown (preserves order)
        try:
            image_urls = extract_all_image_urls(markdown_content)
            logger.debug(f"Extracted {len(image_urls)} image URL(s) from markdown: {image_urls}")
        except ValueError as e:
            logger.error(f"No image URLs found in {prompt_file.name}")
            raise

        # Load prompts (extracts from code block)
        discovery = InputDiscovery(prompt_file.parent, Path("dummy"))
        prompts = discovery.load_prompts(prompt_file)

        logger.info(
            f"Processing combination {ctx.combination_num}/{ctx.total_combinations}: "
            f"{relative_path} + {profile_name}"
        )

        # Update progress if available
        if ctx.progress and ctx.task_id is not None:
            ctx.progress.update(
                ctx.task_id,
                advance=1,
                description=f"[{ctx.combination_num}/{ctx.total_combinations}] {relative_path} + {profile_name}",
            )

        # Create processing context - merge image_input into parameters
        params = ctx.model_info.get("parameters", {}).copy()
        params["image_input"] = image_urls

        context = ProcessingContext(
            prompt_file=prompt_file,
            relative_path=relative_path,
            prompts=prompts,
            model_id=ctx.model_info.get("model_id", ctx.model_info.get("endpoint", "")),
            params=params,  # Now includes image_input array
            pricing=ctx.model_info.get("pricing", {}),
            profile_name=profile_name,
            output_dir=ctx.output_dir,
            prompt_prefix=ctx.model_info.get("prompt_prefix", ""),
            prompt_suffix=ctx.model_info.get("prompt_suffix", ""),
            delay_between_requests=ctx.model_info.get("delay_between_requests", 0),
        )

        # Process with context
        try:
            self._process_with_context(context)
        except Exception as e:
            logger.error(f"Failed processing {relative_path} + {profile_name}: {e}")
            self.failed_count += 1
            success = False
            # Fail-fast philosophy
            raise

        return success

    def _process_with_context(self, context: ProcessingContext) -> None:
        """
        Process prompt using ProcessingContext.

        Args:
            context: ProcessingContext with all required parameters
        """
        # Get pricing
        base_cost = context.pricing.get("base_cost", 0.0)

        # Process the single prompt (entire file content)
        if not context.prompts:
            logger.warning(f"Skipping empty prompt file: {context.relative_path}")
            return

        prompt = context.prompts[0]  # Single prompt from entire file

        # Add prefix and suffix if provided
        prompt = self._apply_prompt_fixes(
            prompt, context.prompt_prefix, context.prompt_suffix
        )

        logger.debug(f"Processing {context.relative_path}: {prompt[:50]}...")

        if self.dry_run:
            logger.info(f"[DRY RUN] Would generate image for {context.relative_path}")
            return

        # Generate and save image
        self._generate_and_save_image(prompt, context, base_cost)

        # Apply delay if specified
        if context.delay_between_requests > 0:
            logger.info(
                f"Waiting {context.delay_between_requests} seconds before next request"
            )
            time.sleep(context.delay_between_requests)

    def _apply_prompt_fixes(self, prompt: str, prefix: str, suffix: str) -> str:
        """Apply prefix and suffix to prompt."""
        if prefix:
            prompt = f"{prefix} {prompt}"
            logger.debug(f"Added prefix to prompt: {prefix}")

        if suffix:
            prompt = f"{prompt} {suffix}"
            logger.debug(f"Added suffix to prompt: {suffix}")

        return prompt

    def _generate_and_save_image(
        self, prompt: str, context: ProcessingContext, base_cost: float
    ) -> None:
        """Generate image and save to disk."""
        try:
            # Generate image with pure parameter pass-through
            response = self.replicate_client.generate_image(
                model_id=context.model_id,
                prompt=prompt,
                params=context.params,  # All profile parameters passed through
                debug=self.debug,
            )

            # Extract result and payload
            result = response["result"]
            payload = response["payload"]

            # Save image
            timestamp = datetime.now().strftime("%H%M%S")

            filename = self.output_writer.save_image(
                image_url=result["images"][0]["url"],
                timestamp=timestamp,
                prompt_file_name=context.prompt_file.stem,
                model_name=context.profile_name,
                output_dir=context.output_dir,
                relative_path=context.relative_path,
                payload=payload if self.save_payloads else None,
            )

            self.processed_count += 1
            self.total_cost += base_cost

            logger.info(f"Saved image: {filename}")

        except Exception as e:
            logger.error(f"Failed to generate image for {context.relative_path}: {e}")
            self.failed_count += 1
            raise

    def get_summary(self) -> Dict[str, Any]:
        """Get processing summary."""
        return {
            "processed": self.processed_count,
            "failed": self.failed_count,
            "total_cost": self.total_cost,
        }
