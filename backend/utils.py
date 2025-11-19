"""
Contains helper functions. This module intentionally groups both
internal helpers and utility functions intended for external reuse.

Author: Anenokil
"""

from typing import Iterable, TYPE_CHECKING

from .types import Word, FormPattern
if TYPE_CHECKING:
    from .entry import Entry


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


def difficulty(entry: 'Entry') -> float:
    """
    Calculate the difficulty of a given entry.

    Args:
        entry: Entry to calculate difficulty for.

    Returns:
        Difficulty score of the entry.
    """

    error_rate = 1 - entry.accuracy
    multiplier = entry.total_att
    score = error_rate * multiplier
    if entry.total_att < 5:
        score += (5 - entry.total_att) / 2
    return score


def has_article(word: Word, articles: Iterable[str]) -> bool:
    """
    Check if the word starts with any of the specified articles.

    Args:
        word: Word to check for article presence.
        articles: Articles to check.

    Returns:
        True if the word begins with any of the provided articles,
        False otherwise.
    """

    for article in articles:
        if word.startswith(article):
            return True
    return False
