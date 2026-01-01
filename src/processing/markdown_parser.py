"""
Markdown parsing utilities for extracting image URLs and prompts.

This module provides functions to parse markdown files and extract:
- Image URLs from markdown image syntax ![alt](URL)
- Text prompts from TEXT SOURCE sections
- Combined image input arrays for API payloads

PRD Reference: Section 05.1, 06.2
"""

import re
from typing import Optional


def extract_image_url(markdown_content: str) -> str:
    """
    Extract first image URL from markdown ![image](URL) syntax.

    Searches for the first occurrence of markdown image syntax and extracts
    the URL. Ignores all metadata lines and subsequent images.

    Args:
        markdown_content: Full markdown file content

    Returns:
        Extracted image URL (https://...)

    Raises:
        ValueError: If no image URL found in markdown

    Example:
        >>> content = "![image](https://example.com/image.jpg)"
        >>> extract_image_url(content)
        'https://example.com/image.jpg'
    """
    # Pattern matches: ![any-text](https://url or http://url)
    # Non-greedy .*? for alt text, [^\)]+ for URL (everything except closing paren)
    pattern = r"!\[.*?\]\((https?://[^\)]+)\)"
    match = re.search(pattern, markdown_content)

    if not match:
        raise ValueError("No image URL found in markdown")

    return match.group(1)


def extract_prompt_text(markdown_content: str) -> str:
    """
    Extract text content from TEXT SOURCE section in markdown.

    Searches for the "**TEXT SOURCE:**" line and extracts all text
    content that follows it. The text must be on the lines after the
    TEXT SOURCE header.

    Args:
        markdown_content: Full markdown file content

    Returns:
        Extracted prompt text (stripped of whitespace)

    Raises:
        ValueError: If no TEXT SOURCE section found or text is empty

    Example:
        >>> content = "**TEXT SOURCE:** frame_0001.txt:\\n\\nA man carries bags.\\n"
        >>> extract_prompt_text(content)
        'A man carries bags.'
    """
    # Split content into lines
    lines = markdown_content.split("\n")

    # Find the TEXT SOURCE line
    text_source_idx = None
    for i, line in enumerate(lines):
        if "**TEXT SOURCE:**" in line:
            text_source_idx = i
            break

    if text_source_idx is None:
        raise ValueError("No TEXT SOURCE section found in markdown")

    # Extract all lines after TEXT SOURCE (skipping empty lines immediately after)
    text_lines = []
    for line in lines[text_source_idx + 1 :]:
        # Start collecting after we skip any initial empty lines
        if not text_lines and not line.strip():
            continue
        text_lines.append(line)

    # Join and strip the result
    content = "\n".join(text_lines).strip()

    if not content:
        raise ValueError("Empty text content after TEXT SOURCE in markdown")

    return content


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
