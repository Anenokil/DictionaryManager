"""
Contains custom exceptions for Dictionary Manager.

Author: Anenokil
"""

from types import GenericAlias
from typing import Any, _GenericAlias, get_origin, get_args


def _type_repr(t: type) -> str:
    if t is Ellipsis:
        return '...'
    if isinstance(t, (GenericAlias, _GenericAlias)):
        origin = get_origin(t)
        args = get_args(t)
        return f'{_type_repr(origin)}[{', '.join(map(_type_repr, args))}]'
    if hasattr(t, '__name__'):
        return t.__name__
    trepr = str(t)
    if trepr.startswith('typing.'):
        return trepr[len('typing.'):]
    return str(t)


class DMError(Exception):
    """Base exception class for all Dictionary Manager errors."""


class BackendError(DMError):
    """Base exception for all backend-related operations."""


class BackendCoreError(BackendError):
    """Exception for core backend functionality errors."""


class DeserializationError(BackendCoreError):
    """Exception raised when data deserialization fails."""


class MissingFieldsError(DeserializationError):
    """
    Exception raised when required fields are missing
    during deserialization.
    """

    def __init__(self, *fields):
        """
        Attributes:
            fields: One or more field names that are missing from the data.
        """

        self.fields = tuple(str(field) for field in fields)

    def __str__(self) -> str:
        if len(self.fields) == 1:
            return f'Missing required field: {self.fields[0]}'
        return f'Missing required fields: {', '.join(self.fields)}'


class FieldTypeError(DeserializationError):
    """
    Exception raised when field types don't match
    expected types during deserialization.
    """

    def __init__(
            self,
            field: Any,
            expected_types: type | tuple[type, ...] | list[type],
            gotten_value: Any,
            gotten_type: type | None = None,
    ):
        """
        Args:
            field: Name of the field with type mismatch.
            expected_types: One or more expected types for this field.
            gotten_value: The actual value that was provided.
            gotten_type: The actual type of the provided value.
        """

        self.field = field
        self.expected_types = (
            expected_types
            if isinstance(expected_types, (list, tuple))
            else [expected_types]
        )
        self.gotten_value = gotten_value
        self.gotten_type = gotten_type if gotten_type else type(gotten_value)

    def __str__(self) -> str:
        expected_types_repr = ', or '.join(
            _type_repr(t) for t in self.expected_types
        )
        gotten_type_repr = _type_repr(self.gotten_type)
        value_repr = repr(self.gotten_value)
        value_max_len = 50
        if len(value_repr) > value_max_len:
            value_repr = value_repr[:value_max_len-3] + '...'

        return (
            f'Field "{self.field}" has invalid type: expected {expected_types_repr}, '
            f'got {gotten_type_repr} (value: {value_repr})'
        )
