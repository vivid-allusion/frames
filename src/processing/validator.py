"""Generic validation logic for processing."""

from typing import Dict, Any, List, Tuple
from pathlib import Path
import re
from loguru import logger
from ..exceptions import ValidationError


class GenericValidator:
    """Validates non-parameter processing requirements."""

    def validate_operational_requirements(
        self, active_models: List[Dict[str, Any]]
    ) -> None:
        """Validate only operational requirements, not parameters."""
        # Only validate that profiles have required structure
        for model in active_models:
            profile_name = model.get("profile_name", "unknown")

            # Check required profile fields exist
            if not model.get("endpoint"):
                error_msg = (
                    f"Profile '{profile_name}' missing required 'endpoint' field"
                )
                logger.error(error_msg)
                raise ValidationError(error_msg)

            # Parameters section is optional - API will validate content
            logger.debug(f"Profile '{profile_name}' operational validation passed")

    def validate_markdown_files(self, prompt_files: List[Tuple[Path, Path]]) -> None:
        """
        Pre-flight validation of all markdown files before processing.

        Validates that each markdown file:
        1. Contains a **TEXT SOURCE:** section
        2. The text content after TEXT SOURCE is not empty

        Args:
            prompt_files: List of tuples (absolute_path, relative_path)

        Raises:
            ValidationError: If any markdown file fails validation
        """
        logger.info(
            f"Pre-flight validation: Checking {len(prompt_files)} markdown files..."
        )

        validation_errors = []

        for abs_path, rel_path in prompt_files:
            try:
                self._validate_single_markdown(abs_path, rel_path)
            except ValidationError as e:
                validation_errors.append(str(e))

        if validation_errors:
            error_summary = "\n".join(f"  - {err}" for err in validation_errors)
            raise ValidationError(
                f"Pre-flight validation failed for {len(validation_errors)} file(s):\n{error_summary}"
            )

        logger.success(
            f"✅ Pre-flight validation passed: All {len(prompt_files)} markdown files are valid"
        )

    def _validate_single_markdown(self, abs_path: Path, rel_path: Path) -> None:
        """
        Validate a single markdown file.

        Args:
            abs_path: Absolute path to markdown file
            rel_path: Relative path for error reporting

        Raises:
            ValidationError: If file fails validation
        """
        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            raise ValidationError(f"{rel_path}: Failed to read file - {e}")

        # Check for TEXT SOURCE section presence
        if "**TEXT SOURCE:**" not in content:
            raise ValidationError(
                f"{rel_path}: No TEXT SOURCE section found. Files must contain '**TEXT SOURCE:**' line"
            )

        # Extract text content after TEXT SOURCE
        lines = content.split("\n")
        text_source_idx = -1
        for i, line in enumerate(lines):
            if "**TEXT SOURCE:**" in line:
                text_source_idx = i
                break

        if text_source_idx == -1:
            # Should never happen since we checked above, but for type safety
            raise ValidationError(
                f"{rel_path}: No TEXT SOURCE section found. Files must contain '**TEXT SOURCE:**' line"
            )

        # Extract content after TEXT SOURCE line
        text_lines = []
        for line in lines[text_source_idx + 1 :]:
            # Skip initial empty lines
            if not text_lines and not line.strip():
                continue
            text_lines.append(line)

        text_content = "\n".join(text_lines).strip()

        if not text_content:
            raise ValidationError(
                f"{rel_path}: Empty text content after TEXT SOURCE. Text must be provided after the TEXT SOURCE line"
            )

        logger.debug(
            f"✓ {rel_path}: Valid (TEXT SOURCE with {len(text_content)} characters)"
        )
