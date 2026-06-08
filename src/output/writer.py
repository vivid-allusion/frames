"""Image writer with validation."""

import requests
import re
import json
from pathlib import Path
from typing import Tuple
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

    def save_image(self, context: ImageSaveContext) -> str:
        """
        Download, validate, and save image using ImageSaveContext.

        Args:
            context: ImageSaveContext with all save parameters

        Returns:
            Saved filename
        """
        print(f"\U0001f4be Starting image save process...")
        print(f"\U0001f4f7 Image URL: {context.image_url}")
        print(f"\u23f0 Timestamp: {context.timestamp}")
        print(f"\U0001f4c1 Prompt file: {context.prompt_file_name}")
        print(f"\U0001f916 Model: {context.model_name}")

        print(f"\u2b07\ufe0f  Downloading image from: {context.image_url}")
        image_data = self._download_image(context.image_url)
        print(f"\u2705 Downloaded {len(image_data)} bytes")

        print(f"\U0001f504 Processing image data...")
        img, format_ext = self._process_image(image_data)
        print(f"\u2705 Image processed, format: {format_ext}")

        save_path = self._determine_save_path(context, format_ext)
        print(f"\U0001f4c1 Save path: {save_path}")

        print(f"\U0001f4be Saving to disk...")
        self._save_to_disk(img, save_path)
        print(f"\u2705 Successfully saved image to: {save_path}")

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
        print(f"🌐 Making HTTP request to: {image_url}")
        print(f"⏰ Timeout: {DEFAULT_IMAGE_DOWNLOAD_TIMEOUT} seconds")

        response = requests.get(image_url, timeout=DEFAULT_IMAGE_DOWNLOAD_TIMEOUT)
        print(f"📊 HTTP Status: {response.status_code}")
        print(f"📦 Content-Type: {response.headers.get('content-type', 'unknown')}")

        response.raise_for_status()

        content_length = len(response.content)
        print(f"📐 Content length: {content_length} bytes")

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
        payload_path = image_path.with_suffix(".md")

        markdown_content = f"""# API Payload

## Image File
`{image_path.name}`

## Request Details
```json
{json.dumps(context.payload, indent=2, ensure_ascii=False)}
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
