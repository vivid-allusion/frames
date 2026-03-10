"""
Markdown parsing utilities for extracting image URLs and prompts.

This module provides functions to parse markdown files and extract:
- Image URLs from line 2 (markdown ![alt](URL) or raw https:// URL)
- Text prompts from line 1

New format:
    Line 1: Text prompt
    Line 2: ![image](URL) or https://...

PRD Reference: Section 05.1, 06.2
"""

import re
from typing import Optional


def extract_image_url(markdown_content: str) -> str:
    """
    Extract image URL from markdown content.

    Supports both markdown syntax ![alt](URL) and raw URLs.
    Searches all lines for the first image URL found.

    Args:
        markdown_content: Full markdown file content

    Returns:
        Extracted image URL (https://...)

    Raises:
        ValueError: If no image URL found

    Example:
        >>> content = "A man carries bags.\\n![image](https://example.com/image.jpg)"
        >>> extract_image_url(content)
        'https://example.com/image.jpg'
        >>> content2 = "Prompt here\\nhttps://example.com/image.jpg"
        >>> extract_image_url(content2)
        'https://example.com/image.jpg'
    """
    lines = markdown_content.split("\n")

    # Try markdown image syntax on any line
    pattern = r"!\[.*?\]\((https?://[^\)]+)\)"

    for line in lines:
        match = re.search(pattern, line)
        if match:
            return match.group(1)

        # Also check for raw URL on this line
        stripped = line.strip()
        if stripped.startswith("http://") or stripped.startswith("https://"):
            return stripped

    raise ValueError("No image URL found in markdown")


def extract_prompt_text(markdown_content: str) -> str:
    """
    Extract text prompt from first line of markdown.

    Takes only the first non-empty line as the prompt text.
    The second line should contain the image URL.

    Args:
        markdown_content: Full markdown file content

    Returns:
        Extracted prompt text (stripped of whitespace)

    Raises:
        ValueError: If no prompt found or content is empty

    Example:
        >>> content = "A man carries bags.\\n![image](https://example.com/img.jpg)"
        >>> extract_prompt_text(content)
        'A man carries bags.'
    """
    lines = markdown_content.split("\n")

    # Find first non-empty line
    for line in lines:
        if line.strip():
            return line.strip()

    raise ValueError("No prompt text found in markdown")


def build_image_input_array(
    markdown_url: str, profile_url: Optional[str] = None
) -> list:
    """
    Build image_input array combining markdown and profile URLs.

    Constructs array format required by API. Always returns array/list,
    never a single string, even with one URL.

    Args:
        markdown_url: Image URL extracted from markdown file
        profile_url: Optional reference image URL from profile YAML

    Returns:
        Array of image URLs: [markdown_url, profile_url] or [markdown_url]

    Example:
        >>> build_image_input_array("https://md.jpg", "https://prof.jpg")
        ['https://md.jpg', 'https://prof.jpg']
        >>> build_image_input_array("https://md.jpg")
        ['https://md.jpg']
    """
    if profile_url:
        return [markdown_url, profile_url]
    return [markdown_url]
