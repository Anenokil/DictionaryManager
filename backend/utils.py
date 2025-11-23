"""
Contains helper functions. This module intentionally groups both
internal helpers and utility functions intended for external reuse.

Author: Anenokil
"""

from types import GenericAlias
from typing import Any, Iterable, Generator, Mapping, _GenericAlias, get_origin, get_args, TYPE_CHECKING

from .types import Word, FormPattern
from .errors import FieldTypeError
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


def validate_field_type(
        field_name: Any,
        field_value: Any,
        expected_types: type | tuple[type, ...] | list[type],
):
    """
    Validate that a field value matches one of the expected types.

    This function supports both plain types and some parameterized/generic
    types (for example: tuple[int, str], list[str], dict[str, int], etc.).

    Args:
        field_name: Identifier of the field (used in error messages).
        field_value: The value to validate.
        expected_types: A type, or a tuple/list of types. Elements may be
            parameterized generics (built-in or from typing module).

    Raises:
        FieldTypeError: If the value does not conform to any of the expected
            types.
        NotImplementedError: If validation for a particular container/generic
            type is not implemented.
    """

    # If a single expected type is provided, convert it to a tuple
    if not isinstance(expected_types, (tuple, list)):
        expected_types = (expected_types,)

    # Build a tuple of base types (origins for generics, or the type itself
    # for non-generic) and ensure the value is an instance of at least one
    # of them. If not, raise an error
    base_types = tuple(
        get_origin(t) if isinstance(t, (GenericAlias, _GenericAlias)) else t
        for t in expected_types
    )
    if not isinstance(field_value, base_types):
        raise FieldTypeError(field_name, expected_types, field_value)

    # If the value matches any non-generic expected type, validation passes
    non_generic_types = tuple(
        t for t in expected_types
        if not isinstance(t, (GenericAlias, _GenericAlias))
    )
    if isinstance(field_value, non_generic_types):
        return

    # For generic expected types, keep only those generics whose origin
    # matches the runtime type of the field value
    generic_types = tuple(
        t for t in expected_types
        if isinstance(t, (GenericAlias, _GenericAlias))
        and isinstance(field_value, get_origin(t))
    )

    # Validate elements according to container type
    if isinstance(field_value, Generator):
        raise NotImplementedError(f'Validation for Generator is not implemented')
    if isinstance(field_value, tuple):
        for t in generic_types:
            elem_types = get_args(t)
            if Ellipsis in elem_types:
                try:
                    for elem in field_value:
                        validate_field_type(field_name, elem, elem_types[0])
                except FieldTypeError:
                    continue
            else:
                if len(field_value) != len(elem_types):
                    continue
                try:
                    for elem, type_elem in zip(field_value, elem_types):
                        validate_field_type(field_name, elem, type_elem)
                except FieldTypeError:
                    continue
            return
        raise FieldTypeError(field_name, expected_types, field_value, gotten_type=type(field_value)[Any, ...])
    if isinstance(field_value, Mapping):
        for t in generic_types:
            key_types, val_types = get_args(t)
            try:
                for k, v in field_value.items():
                    validate_field_type(field_name, k, key_types)
                    validate_field_type(field_name, v, val_types)
            except FieldTypeError:
                continue
            return
        raise FieldTypeError(field_name, expected_types, field_value, gotten_type=type(field_value)[Any, Any])
    if isinstance(field_value, Iterable):
        for t in generic_types:
            elem_types = get_args(t)
            try:
                for elem in field_value:
                    validate_field_type(field_name, elem, elem_types)
            except FieldTypeError:
                continue
            return
        raise FieldTypeError(field_name, expected_types, field_value, gotten_type=type(field_value)[Any])
    raise NotImplementedError(f'Validation for {type(field_value)} generic is not implemented')
