"""
Text cleaning utilities for scraped content

Provides functions to clean and normalize extracted text.
"""

import re


def clean_text(text: str) -> str:
    """
    Clean and normalize text extracted from web pages.

    Args:
        text: Raw text to clean

    Returns:
        str: Cleaned text

    Operations performed:
    - Remove excessive whitespace
    - Normalize line breaks
    - Remove special characters (optional)
    - Trim leading/trailing whitespace
    """
    if not text:
        return ""

    # Normalize line breaks
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove excessive whitespace (more than 2 consecutive spaces)
    text = re.sub(r" {3,}", "  ", text)

    # Remove excessive line breaks (more than 2 consecutive newlines)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Trim leading/trailing whitespace
    text = text.strip()

    return text


def truncate_text(text: str, max_length: int) -> tuple[str, bool]:
    """
    Truncate text to a maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length in characters

    Returns:
        tuple: (truncated_text, was_truncated)
    """
    if len(text) <= max_length:
        return text, False

    # Truncate at max_length
    truncated = text[:max_length]

    # Try to truncate at last sentence boundary
    last_period = truncated.rfind(".")
    if last_period > max_length * 0.8:  # Only if we're not losing too much
        truncated = truncated[: last_period + 1]

    return truncated, True


def extract_title_from_content(content: str, max_length: int = 200) -> str:
    """
    Extract a title from content if no title is available.

    Args:
        content: Article content
        max_length: Maximum title length

    Returns:
        str: Extracted title
    """
    if not content:
        return "Untitled Article"

    # Take first sentence or first line
    lines = content.split("\n")
    first_line = lines[0] if lines else content

    # Limit to max_length
    if len(first_line) > max_length:
        first_line = first_line[:max_length].rsplit(" ", 1)[0] + "..."

    return first_line.strip()
