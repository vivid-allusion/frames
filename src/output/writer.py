"""Image writer with validation."""

import requests
import re
import json
from pathlib import Path
from typing import Any, Optional, Dict, Union, Tuple
from datetime import datetime
from PIL import Image
from io import BytesIO
from loguru import logger
from .context import ImageSaveContext
from ..constants import DEFAULT_IMAGE_DOWNLOAD_TIMEOUT


class OutputWriter:
    """Handle image saving and validation."""

    def __init__(self, output_dir: Path, force_png: bool = False):
        """
        Initialize output writer.

        Args:
            output_dir: Base output directory
            force_png: Convert all images to PNG format
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.force_png = force_png

    def save_image(
        self,
        image_url: str,
        timestamp: str,
        prompt_file_name: str,
        model_name: str,
        output_dir: Optional[Path] = None,
        relative_path: Optional[Path] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Download, validate, and save image using context.

        Args:
            image_url: URL of generated image
            timestamp: Timestamp string (HHMMSS)
            prompt_file_name: Name of source prompt file (without extension)
            model_name: Model nickname
            output_dir: Optional specific output directory
            relative_path: Optional relative path from input directory
            payload: Optional API payload to save as JSON

        Returns:
            Saved filename
        """
        # Create context for cleaner parameter passing
        context = ImageSaveContext(
            image_url=image_url,
            timestamp=timestamp,
            prompt_file_name=prompt_file_name,
            model_name=model_name,
            output_dir=output_dir if output_dir else self.output_dir,
            relative_path=relative_path,
            payload=payload,
        )

        # Process image through pipeline
        image_data = self._download_image(context.image_url)
        img, format_ext = self._process_image(image_data)
        save_path = self._determine_save_path(context, format_ext)
        self._save_to_disk(img, save_path)

        # Save payload if provided
        if context.payload:
            self._save_payload(context, save_path)

        return str(save_path)

    def _download_image(self, image_url: str) -> bytes:
        """
        Download image from URL.

        Args:
            image_url: URL to download from

        Returns:
            Image data as bytes

        Raises:
            requests.RequestException: If download fails
        """
        response = requests.get(image_url, timeout=DEFAULT_IMAGE_DOWNLOAD_TIMEOUT)
        response.raise_for_status()
        return response.content

    def _process_image(self, image_data: bytes) -> Tuple[Image.Image, str]:
        """
        Validate and optionally convert image.

        Args:
            image_data: Raw image bytes

        Returns:
            Tuple of (PIL Image, format extension)

        Raises:
            ValueError: If image is invalid
        """
        # Validate image
        try:
            img = Image.open(BytesIO(image_data))
            img.verify()
            # Re-open for actual processing (verify closes the file)
            img = Image.open(BytesIO(image_data))
        except Exception as e:
            raise ValueError(f"Invalid image received: {e}")

        # Determine format
        original_format = img.format.lower() if img.format else "png"

        # Convert to PNG if needed
        if self.force_png and original_format != "png":
            img, format_ext = self._convert_to_png(img, original_format)
        else:
            format_ext = original_format

        return img, format_ext

    def _convert_to_png(
        self, img: Image.Image, original_format: str
    ) -> Tuple[Image.Image, str]:
        """
        Convert image to PNG format.

        Args:
            img: PIL Image object
            original_format: Original format name

        Returns:
            Tuple of (converted Image, 'png')
        """
        logger.debug(f"Converting {original_format.upper()} to PNG")
        png_buffer = BytesIO()

        try:
            # Save to PNG format (preserves alpha if present)
            img.save(png_buffer, "PNG")

            # Reload as PNG
            png_buffer.seek(0)
            img = Image.open(png_buffer)
            logger.info(f"Converted {original_format.upper()} to PNG format")

            return img, "png"

        except Exception as e:
            logger.error(f"Failed to convert image to PNG: {e}")
            raise ValueError(f"PNG conversion failed: {e}")

    def _determine_save_path(self, context: ImageSaveContext, format_ext: str) -> Path:
        """
        Determine full save path for image.

        Args:
            context: ImageSaveContext with all parameters
            format_ext: File extension

        Returns:
            Full path for saving
        """
        # Build filename: filename-YYMMDD_HHMMSS.png format (PRD Section 04.7)
        # Get date prefix from output_dir (YYMMDD format)
        date_str = (
            context.output_dir.name
            if context.output_dir.name.isdigit() and len(context.output_dir.name) >= 6
            else datetime.now().strftime("%y%m%d")
        )
        filename = (
            f"{context.prompt_file_name}-{date_str}_{context.timestamp}.{format_ext}"
        )

        # Create nested directory structure if needed
        save_dir = context.output_dir

        if context.relative_path:
            parent_path = context.relative_path.parent
            if parent_path != Path("."):
                sanitized_path = self._sanitize_path(str(parent_path))
                save_dir = save_dir / sanitized_path
                save_dir.mkdir(parents=True, exist_ok=True)

        return save_dir / filename

    def _save_to_disk(self, img: Image.Image, save_path: Path) -> None:
        """
        Save image to disk.

        Args:
            img: PIL Image object
            save_path: Path to save to
        """
        img.save(save_path)
        logger.info(f"Saved valid image: {save_path}")

    def _save_payload(self, context: ImageSaveContext, image_path: Path) -> None:
        """
        Save API payload as Markdown file.

        Args:
            context: ImageSaveContext with payload
            image_path: Path where image was saved
        """
        payload_path = image_path.with_suffix(".md")

        # Check if payload has filtering information
        payload_data = context.payload
        has_filtering_info = (
            isinstance(payload_data, dict) and "intended_request" in payload_data
        )

        if has_filtering_info:
            # New format with filtering detection
            intended = payload_data.get("intended_request", {})
            actual = payload_data.get("actual_request", {})
            filtering_detected = payload_data.get("api_filtering_detected", False)

            markdown_content = f"""# API Payload Analysis

## Image File
`{image_path.name}`

## Parameter Filtering Status
{"⚠️ **API FILTERING DETECTED**" if filtering_detected else "✅ **No Filtering Detected**"}

{f"The API likely filtered out unsupported parameters. See comparison below." if filtering_detected else "All intended parameters appear to be supported by the model."}

## Intended Request (What We Tried to Send)
```json
{json.dumps(intended, indent=2, ensure_ascii=False)}
```

## Actual Request (What Was Actually Sent)
```json
{json.dumps(actual, indent=2, ensure_ascii=False)}
```

{f"## ⚠️ Potential Issues\n- Some parameters may not be supported by the `{payload_data.get('model_id', 'unknown')}` model\n- Check model documentation for supported parameters\n- Consider using a different model if image inputs are required\n" if filtering_detected else ""}
## Timestamp
Generated at: {context.timestamp}
"""
        else:
            # Legacy format
            markdown_content = f"""# API Payload

## Image File
`{image_path.name}`

## Request Details
```json
{json.dumps(payload_data, indent=2, ensure_ascii=False)}
```

## Timestamp
Generated at: {context.timestamp}
"""

        with open(payload_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        logger.debug(f"Saved payload to {payload_path}")

    def _sanitize_path(self, path_str: str) -> str:
        """
        Sanitize path string for filesystem safety.

        Args:
            path_str: Path string to sanitize

        Returns:
            Sanitized path string
        """
        # Replace problematic characters with underscores
        problematic_chars = r"[\'()[\]{}@#&]"
        sanitized = re.sub(problematic_chars, "_", path_str)

        # Replace multiple underscores with single
        sanitized = re.sub(r"_+", "_", sanitized)

        # Remove leading/trailing underscores from each component
        parts = sanitized.split("/")
        parts = [p.strip("_") for p in parts if p]

        return "/".join(parts)

    def write_report(self, content: str, filename: str) -> None:
        """
        Write a markdown report to output directory.

        Args:
            content: Report content
            filename: Report filename
        """
        report_path = self.output_dir / filename
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Report saved: {report_path}")
