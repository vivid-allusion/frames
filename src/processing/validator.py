"""Generic validation logic for processing."""

from typing import List, Tuple
from pathlib import Path
import re
from loguru import logger
from ..exceptions import ValidationError


class GenericValidator:
    """Validates non-parameter processing requirements."""

    def validate_markdown_files(self, prompt_files: List[Tuple[Path, Path]]) -> None:
        """
        Pre-flight validation of all markdown files before processing.

        Validates that each markdown file:
        1. Has at least 2 lines
        2. Line 1 contains non-empty prompt text
        3. Line 2 contains a valid image URL (markdown syntax or raw https://)

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

        lines = content.split("\n")

        if len(lines) < 2:
            raise ValidationError(
                f"{rel_path}: Invalid format. Need at least 2 lines (prompt + image URL)"
            )

        line1 = lines[0].strip()
        if not line1:
            raise ValidationError(
                f"{rel_path}: Line 1 is empty. First line must contain the prompt text"
            )

        line2 = lines[1].strip()
        if not line2:
            raise ValidationError(
                f"{rel_path}: Line 2 is empty. Second line must contain the image URL"
            )

        # Check for valid URL (markdown syntax or raw)
        url_pattern = r"(!\[.*?\]\()?https?://[^\s\)]+(\))?"
        if not re.match(url_pattern, line2):
            raise ValidationError(
                f"{rel_path}: Line 2 does not contain a valid image URL. Use ![alt](https://...) or raw https:// URL"
            )

        logger.debug(
            f"✓ {rel_path}: Valid ({len(line1)} char prompt, image URL present)"
        )
