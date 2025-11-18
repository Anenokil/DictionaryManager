"""
Contains helper functions. This module intentionally groups both
internal helpers and utility functions intended for external reuse.

Author: Anenokil
"""

from .types import FormPattern


def pattern_to_str(pattern: FormPattern) -> str:
    """
    Convert a form pattern to a readable string.

    Joins non-empty category values with commas, skipping empty values.

    Args:
        pattern: Form pattern tuple containing category values.

    Returns:
        Comma-separated string of non-empty category values.
    """

    return ', '.join(token for token in pattern if token)
