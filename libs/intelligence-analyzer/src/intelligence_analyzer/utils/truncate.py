"""
Content truncation utilities

Provides functions to truncate content to fit within token limits.
"""


def truncate_content(content: str, max_chars: int = 16000) -> tuple[str, bool]:
    """
    Truncate content to a maximum character count (approximately 4000 tokens).

    Args:
        content: Content to truncate
        max_chars: Maximum character count (default: 16000, ~4000 tokens)

    Returns:
        tuple: (truncated_content, was_truncated)

    Note:
        Uses ~4 characters per token as approximation.
        Actual token count may vary.
    """
    if len(content) <= max_chars:
        return content, False

    # Truncate to max_chars
    truncated = content[:max_chars]

    # Try to truncate at last paragraph boundary
    last_paragraph = truncated.rfind("\n\n")
    if last_paragraph > max_chars * 0.8:  # Only if we're not losing too much
        truncated = truncated[:last_paragraph]
    else:
        # Try to truncate at last sentence boundary
        last_sentence = truncated.rfind(".")
        if last_sentence > max_chars * 0.8:
            truncated = truncated[: last_sentence + 1]

    return truncated, True
