"""
Markdown parsing utilities for extracting image URLs and prompts.

This module provides functions to parse markdown files and extract:
- Image URLs from markdown image syntax ![alt](URL)
- Text prompts from code blocks
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
    Extract text content from first code block in markdown.

    Searches for the first code block (triple backticks) and extracts the
    text content. Ignores language identifier (can be 'text', 'python', or none).

    Args:
        markdown_content: Full markdown file content

    Returns:
        Extracted prompt text (stripped of whitespace)

    Raises:
        ValueError: If no code block found or code block is empty

    Example:
        >>> content = "```text\\nA man carries bags.\\n```"
        >>> extract_prompt_text(content)
        'A man carries bags.'
    """
    # Pattern matches: ```optional-language\ncontent\n```
    # [a-zA-Z]* allows optional language identifier
    # (.*?) captures content non-greedily
    # re.DOTALL makes . match newlines for multiline code blocks
    pattern = r"```[a-zA-Z]*\n(.*?)\n```"
    match = re.search(pattern, markdown_content, re.DOTALL)

    if not match:
        raise ValueError("No code block found in markdown")

    content = match.group(1).strip()
    if not content:
        raise ValueError("Empty code block in markdown")

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
